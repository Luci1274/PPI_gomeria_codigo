from datetime import datetime, date
import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import pymysql
from config import Config

#------------------------------------------------------------------------
# TABLA VENTA
#------------------------------------------------------------------------

class Venta:

    @staticmethod
    def registrar(
        id_cliente,
        id_empleado,
        lista_items,
        id_metodo_pago=1,  # <-- Recibe el método de pago elegido
        numero_factura=1,
        iva=21.0,
        descuento=0.0,
        estado=1, #Es el estado de la venta 1 = completo, 0= deuda
        plazo_pago=0 #la cantidad de dias que el 0 tiene para pagar
    ):
        """Registra la Venta, sus Ítems, descuenta Stock e inserta el registro en el historial de pagos."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cantidades_por_producto = {}
                for item in lista_items:
                    id_producto = int(item["idproducto_servicio"])
                    cantidad = int(item["cantidad"])
                    if id_producto <= 0 or cantidad <= 0:
                        raise ValueError("Los identificadores y cantidades deben ser positivos.")
                    cantidades_por_producto[id_producto] = (
                        cantidades_por_producto.get(id_producto, 0) + cantidad
                    )

                if not cantidades_por_producto:
                    raise ValueError("El carrito de venta no puede estar vacío.")

                items_sanitizados = [
                    {
                        "idproducto_servicio": id_producto,
                        "cantidad": cantidad
                    }
                    for id_producto, cantidad in cantidades_por_producto.items()
                ]

                # 1. Validar stock disponible
                ids_productos = [item["idproducto_servicio"] for item in items_sanitizados]

                format_strings = ",".join(["%s"] * len(ids_productos))
                sql_check = f"""
                    SELECT idproducto_servicio, nombre, cantidad_actual, tipo, precio, activo
                    FROM producto_servicio
                    WHERE idproducto_servicio IN ({format_strings})
                    FOR UPDATE;
                """
                cursor.execute(sql_check, ids_productos)
                productos_db = {
                    p["idproducto_servicio"]: p for p in cursor.fetchall()
                }

                if len(productos_db) != len(ids_productos):
                    raise ValueError("Uno o más artículos ya no existen en el inventario.")

                subtotal = Decimal("0.00")
                actualizaciones_stock = []
                for item in items_sanitizados:
                    prod_id = item["idproducto_servicio"]
                    cantidad = item["cantidad"]
                    producto = productos_db[prod_id]
                    if not producto["activo"]:
                        raise ValueError(f"El artículo '{producto['nombre']}' está inactivo.")

                    try:
                        precio_unitario = Decimal(str(producto["precio"]))
                    except (InvalidOperation, TypeError):
                        raise ValueError(f"El precio de '{producto['nombre']}' no es válido.")
                    if not precio_unitario.is_finite() or precio_unitario < 0:
                        raise ValueError(f"El precio de '{producto['nombre']}' no es válido.")

                    item["precio_unitario"] = precio_unitario
                    subtotal += precio_unitario * cantidad

                    if str(producto["tipo"]).strip().casefold() != "servicio":
                        if producto["cantidad_actual"] < cantidad:
                            raise ValueError(
                                f"Stock insuficiente para '{producto['nombre']}'. "
                                f"Disponibles: {producto['cantidad_actual']}, Solicitados: {cantidad}"
                            )
                        actualizaciones_stock.append((cantidad, prod_id))

                try:
                    descuento_decimal = Decimal(str(descuento))
                except (InvalidOperation, TypeError):
                    raise ValueError("El descuento no es válido.")
                if (
                    not descuento_decimal.is_finite()
                    or descuento_decimal < 0
                    or descuento_decimal > subtotal
                ):
                    raise ValueError("El descuento debe estar entre cero y el subtotal.")

                precio_total = (subtotal - descuento_decimal).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                total_productos = sum(item["cantidad"] for item in items_sanitizados)

                # 2. Insertar la cabecera de la venta
                sql_venta = """
                    INSERT INTO venta (
                        numero_factura, fecha_emision_factura, descuento, iva, 
                        cantidad_total_productos, precio_total, idcliente, idempleado, activa, estado
                    ) VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, 1, %s);
                """
                cursor.execute(
                    sql_venta,
                    (
                        numero_factura,
                        descuento,
                        iva,
                        total_productos,
                        precio_total,
                        id_cliente,
                        id_empleado,
                        estado
                    ),
                )
                id_venta = cursor.lastrowid

                # 3. Insertar ítems
                sql_items = """
                    INSERT INTO item_venta (
                        idventa, idproducto_servicio, precio_unitario, cantidad
                    ) VALUES (%s, %s, %s, %s);
                """
                valores_items = [
                    (
                        id_venta,
                        item["idproducto_servicio"],
                        str(item["precio_unitario"]),
                        item["cantidad"],
                    )
                    for item in items_sanitizados
                ]
                cursor.executemany(sql_items, valores_items)

                # 4. Descontar stock
                sql_stock = """
                    UPDATE producto_servicio 
                    SET cantidad_actual = cantidad_actual - %s 
                    WHERE idproducto_servicio = %s;
                """
                if actualizaciones_stock:
                    cursor.executemany(sql_stock, actualizaciones_stock)

                # 5. Insertar en historial_pago (Coincidiendo con la estructura de la imagen)
                sql_pago = """
                    INSERT INTO historial_pago_cliente (
                        fecha, hora, monto, idmetodos_pago, plazo_pago, idventa
                    ) VALUES (CURDATE(), CURTIME(), %s, %s, %s, %s);
                """
                cursor.execute(sql_pago, (str(precio_total), id_metodo_pago, plazo_pago, id_venta))

            conexion.commit()
            print(f"Venta #{id_venta} y su pago fueron registrados exitosamente.")
            return id_venta

        except ValueError:
            conexion.rollback()
            raise
        except Exception as e:
            conexion.rollback()
            print(f"Error en la transacción de la venta: {e}")
            return None

        finally:
            conexion.close()

    @staticmethod
    def obtener_ventas_paginadas(
        busqueda=None,
        filtro_fecha="hoy",
        fecha_inicio=None,
        fecha_fin=None,
        pagina=1,
        limite=20,
    ):
        """Lee el listado de ventas aplicando filtros dinámicos, paginación

        y devuelve métricas acordes a la búsqueda realizada.
        """
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:

                # 1. Construcción dinámica de la cláusula WHERE y parámetros
                condiciones = ["v.activa = 1"]
                parametros = []

                # Filtro por texto (Buscador)
                if busqueda and busqueda.strip():
                    terminos = busqueda.split()
                    condiciones.append(
                        "("
                        + " AND ".join(
                            "(c.nombre LIKE %s OR c.apellido LIKE %s)"
                            for _ in terminos
                        )
                        + ")"
                    )
                    for termino in terminos:
                        patron = f"%{termino}%"
                        parametros.extend([patron, patron])

                # Filtro por rango específico o predefinido
                if fecha_inicio and fecha_fin:
                    condiciones.append(
                        "v.fecha_emision_factura BETWEEN %s AND %s"
                    )
                    parametros.extend(
                        [f"{fecha_inicio} 00:00:00", f"{fecha_fin} 23:59:59"]
                    )
                elif filtro_fecha == "hoy":
                    condiciones.append("v.fecha_emision_factura >= CURDATE()")
                elif filtro_fecha == "semana":
                    condiciones.append(
                        "v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
                    )
                elif filtro_fecha == "mes":
                    condiciones.append(
                        "v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
                    )
                elif filtro_fecha == "anio":
                    condiciones.append(
                        "v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
                    )

                where_clause = " WHERE " + " AND ".join(condiciones)

                # 2. Obtener métricas agregadas (sincronizadas con los filtros)
                sql_totales = f"""
                    SELECT 
                        COUNT(v.idventa) AS total_ventas,
                        IFNULL(SUM(v.cantidad_total_productos), 0) AS total_productos,
                        IFNULL(SUM(v.precio_total), 0) AS total_monto
                    FROM venta AS v
                    LEFT JOIN cliente AS c ON v.idcliente = c.idcliente
                    {where_clause}
                """
                cursor.execute(sql_totales, parametros)
                res_totales = cursor.fetchone() or {}

                total_ventas = res_totales.get("total_ventas", 0)
                total_productos = int(res_totales.get("total_productos", 0))
                total_monto = float(res_totales.get("total_monto", 0.0))

                # Cálculo de paginación
                pagina = max(1, int(pagina))
                limite = max(1, int(limite))
                total_paginas = (
                    math.ceil(total_ventas / limite) if total_ventas > 0 else 1
                )
                offset = (pagina - 1) * limite

                # 3. Consulta de las ventas paginadas
                sql_ventas = f"""
                    SELECT 
                        v.idventa,
                        v.numero_factura,
                        v.fecha_emision_factura AS fecha,
                        CONCAT(IFNULL(c.nombre, 'Consumidor'), ' ', IFNULL(c.apellido, 'Final')) AS cliente,
                        v.cantidad_total_productos,
                        v.precio_total
                    FROM venta AS v
                    LEFT JOIN cliente AS c ON v.idcliente = c.idcliente
                    {where_clause}
                    ORDER BY v.fecha_emision_factura DESC, v.idventa DESC
                    LIMIT %s OFFSET %s;
                """

                # Duplicamos la lista de parámetros para agregar LIMIT y OFFSET
                parametros_ventas = parametros.copy()
                parametros_ventas.extend([limite, offset])

                cursor.execute(sql_ventas, parametros_ventas)
                ventas = cursor.fetchall()

                # Formatear objetos tipo date/datetime a string para evitar fallos de JSON
                for v in ventas:
                    if isinstance(v.get("fecha"), (datetime, date)):
                        v["fecha"] = v["fecha"].strftime("%d/%m/%Y %H:%M")
                    v["precio_total"] = float(v.get("precio_total", 0))

                return {
                    "ventas": ventas,
                    "paginacion": {
                        "pagina_actual": pagina,
                        "limite": limite,
                        "total_registros": total_ventas,
                        "total_paginas": total_paginas,
                    },
                    "resumen": {
                        "total_ventas": total_ventas,
                        "total_productos": total_productos,
                        "total_monto": total_monto,
                    },
                    "Exito": True,
                }

        except pymysql.MySQLError as e:
            print(f"Error al consultar las ventas: {e}")
            return {
                "ventas": [],
                "paginacion": {
                    "pagina_actual": 1,
                    "limite": limite,
                    "total_registros": 0,
                    "total_paginas": 0,
                },
                "resumen": {
                    "total_ventas": 0,
                    "total_productos": 0,
                    "total_monto": 0.0,
                },
                "Exito": False
            }
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_venta):
        """Obtiene la cabecera de la venta y la lista de sus productos para la pantalla de detalle."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql_cabecera = """
                    SELECT 
                        v.idventa,
                        v.numero_factura,
                        DATE(v.fecha_emision_factura) AS fecha,
                        v.descuento,
                        v.cantidad_total_productos,
                        v.precio_total,
                        CONCAT (c.nombre, ' ', c.apellido) AS nombre_cliente,
                        c.numero_tel,
                        c.mail
                    FROM venta AS v
                    LEFT JOIN cliente AS c ON v.idcliente = c.idcliente
                    WHERE v.idventa = %s;
                """
                cursor.execute(sql_cabecera, (id_venta,))
                venta = cursor.fetchone()

                if not venta:
                    return [], [], False

                sql_items = """
                    SELECT 
                        iv.id_item_venta,
                        iv.cantidad,
                        iv.precio_unitario,
                        ps.nombre AS producto_nombre,
                        ps.imagen_producto
                    FROM item_venta AS iv
                    INNER JOIN producto_servicio AS ps ON iv.idproducto_servicio = ps.idproducto_servicio
                    WHERE iv.idventa = %s;
                """
                cursor.execute(sql_items, (id_venta,))
                items = cursor.fetchall()

                return venta, items, True

        except Exception as e:
            print(f"Error al obtener el detalle de la venta #{id_venta}: {e}")
            return [], [], False
        finally:
            conexion.close()
        
    @staticmethod
    def anular(id_venta):
        """Anula una venta y restituye el stock de los artículos que no son servicios."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT activa FROM venta WHERE idventa = %s;", (id_venta,)
                )
                venta = cursor.fetchone()

                if not venta:
                    print(f"La venta ID {id_venta} no existe.")
                    return False

                if venta["activa"] == 0:
                    print(f"La venta ID {id_venta} ya se encuentra anulada.")
                    return False

                sql_obtener_items = """
                    SELECT idproducto_servicio, cantidad 
                    FROM item_venta 
                    WHERE idventa = %s;
                """
                cursor.execute(sql_obtener_items, (id_venta,))
                items = cursor.fetchall()

                sql_restituir_stock = """
                    UPDATE producto_servicio 
                    SET cantidad_actual = cantidad_actual + %s 
                    WHERE idproducto_servicio = %s
                      AND LOWER(TRIM(tipo)) != 'servicio';
                """
                valores_stock = [
                    (item["cantidad"], item["idproducto_servicio"]) for item in items
                ]

                if valores_stock:
                    cursor.executemany(sql_restituir_stock, valores_stock)

                sql_anular = "UPDATE venta SET activa = 0 WHERE idventa = %s;"
                cursor.execute(sql_anular, (id_venta,))

            conexion.commit()
            print(f"Venta #{id_venta} anulada exitosamente y stock restituido.")
            return True

        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al anular la venta ID {id_venta}: {e}")
            return False

        finally:
            conexion.close()
            
    @staticmethod
    def obtener_datos_inicio_venta():
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT p.idproducto_servicio, p.nombre, p.medidas, p.tipo, p.precio, p.imagen_producto, p.cantidad_actual FROM producto_servicio AS p WHERE activo = 1;")
                productos = cursor.fetchall()

                cursor.execute("SELECT DISTINCT tipo FROM producto_servicio WHERE activo = 1;")
                tipos = cursor.fetchall()
                
                cursor.execute("SELECT idcliente, nombre, apellido FROM cliente WHERE activo = 1")
                cliente = cursor.fetchall()
                
                cursor.execute("SELECT idmetodos_pago, nombre FROM metodos_pago WHERE activo = 1")
                metodos_pago = cursor.fetchall()
                
                return productos, tipos, cliente, metodos_pago, True
        except pymysql.MySQLError as e:
                    conexion.rollback()
                    print(f"Error al crear producto/servicio: {e}")
                    return [], [], [], [], False
                
        finally:
            conexion.close()
