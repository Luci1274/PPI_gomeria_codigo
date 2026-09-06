from datetime import datetime, date
import math
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
        numero_factura=1,
        iva=21,
        descuento=0,
        precio_total=0.0,
        total_productos=0,
    ):
        """Registra la Venta, sus Ítems y descuenta Stock solo si hay disponibilidad suficiente."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                # 1. Validar stock disponible previo a la inserción
                ids_productos = [item["idproducto_servicio"] for item in lista_items]

                if ids_productos:
                    format_strings = ",".join(["%s"] * len(ids_productos))
                    sql_check = f"""
                        SELECT idproducto_servicio, nombre, cantidad_actual, tipo 
                        FROM producto_servicio 
                        WHERE idproducto_servicio IN ({format_strings});
                    """
                    cursor.execute(sql_check, ids_productos)
                    productos_db = {
                        p["idproducto_servicio"]: p for p in cursor.fetchall()
                    }

                    # Verificar stock ítem por ítem
                    for item in lista_items:
                        prod_id = item["idproducto_servicio"]
                        cant_pedida = int(item["cantidad"])

                        if prod_id in productos_db:
                            prod = productos_db[prod_id]
                            if (
                                prod["tipo"] == "producto"
                                and prod["cantidad_actual"] < cant_pedida
                            ):
                                raise ValueError(
                                    f"Stock insuficiente para '{prod['nombre']}'. Disponibles: {prod['cantidad_actual']}, Solicitados: {cant_pedida}"
                                )

                # 2. Insertar la cabecera de la venta
                sql_venta = """
                    INSERT INTO venta (
                        numero_factura, fecha_emision_factura, descuento, iva, cantidad_total_productos, precio_total, idcliente, idempleado, activa
                    ) VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, 1);
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
                        item["precio_unitario"],
                        item["cantidad"],
                    )
                    for item in lista_items
                ]
                cursor.executemany(sql_items, valores_items)

                # 4. Descontar stock
                sql_stock = """
                    UPDATE producto_servicio 
                    SET cantidad_actual = cantidad_actual - %s 
                    WHERE idproducto_servicio = %s AND tipo = 'producto';
                """
                valores_stock = [
                    (item["cantidad"], item["idproducto_servicio"])
                    for item in lista_items
                ]
                cursor.executemany(sql_stock, valores_stock)

            conexion.commit()
            print(f"Venta #{id_venta} procesada exitosamente.")
            return id_venta

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
                    condiciones.append("""( 
                        c.nombre LIKE %s 
                        OR c.apellido LIKE %s
                        OR CONCAT(c.nombre, ' ', c.apellido) LIKE %s
                    )""")
                    patron = f"%{busqueda.strip()}%"
                    parametros.extend([patron] * 5)

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
                        v.fecha_emision_factura,
                        v.descuento,
                        v.cantidad_total_productos,
                        v.precio_total,
                        CONCAT(IFNULL(c.nombre, 'Consumidor'), ' ', IFNULL(c.apellido, 'Final')) AS nombre_cliente
                    FROM venta AS v
                    LEFT JOIN cliente AS c ON v.idcliente = c.idcliente
                    WHERE v.idventa = %s;
                """
                cursor.execute(sql_cabecera, (id_venta,))
                venta = cursor.fetchone()

                if not venta:
                    return None

                sql_items = """
                    SELECT 
                        iv.id_item_venta,
                        iv.cantidad,
                        iv.precio_unitario,
                        (iv.cantidad * iv.precio_unitario) AS subtotal,
                        ps.nombre AS producto_nombre,
                        ps.imagen_producto
                    FROM item_venta AS iv
                    INNER JOIN producto_servicio AS ps ON iv.idproducto_servicio = ps.idproducto_servicio
                    WHERE iv.idventa = %s;
                """
                cursor.execute(sql_items, (id_venta,))
                venta["items"] = cursor.fetchall()

                return venta

        except Exception as e:
            print(f"Error al obtener el detalle de la venta #{id_venta}: {e}")
            return None
        finally:
            conexion.close()
        
    @staticmethod
    def anular(id_venta):
        """Anula de forma lógica una venta y reintegra las cantidades al stock de productos."""
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
                    WHERE idproducto_servicio = %s AND tipo = 'producto';
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
                
                return productos, tipos, cliente, True
        except pymysql.MySQLError as e:
                    conexion.rollback()
                    print(f"Error al crear producto/servicio: {e}")
                    return [], [], [], False
                
        finally:
            conexion.close()
