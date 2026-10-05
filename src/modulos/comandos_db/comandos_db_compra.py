from datetime import datetime, date
import math
import pymysql
from config import Config
#------------------------------------------------------------------------
# TABLA COMPRA
#------------------------------------------------------------------------

class Compra:
    @staticmethod
    def registrar(
        id_proveedor,
        listado_items,
        total_productos,
        fecha=None,
    ):
        """Registra una compra, sus ítems y el ingreso de stock."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                items_sanitizados = [
                    {
                        "idproducto_servicio": item["idproducto_servicio"],
                        "cantidad": item["cantidad"],
                    }
                    for item in listado_items
                ]

                sql_compra = """
                    INSERT INTO compra (fecha, horas, cantidad_total, idproveedor, activo)
                    VALUES (%s, %s, %s, %s, 1);
                """
                cursor.execute(
                    sql_compra,
                    (
                        fecha or datetime.now().date(),
                        datetime.now().time(),
                        total_productos,
                        id_proveedor,
                    )
                )
                id_compra = cursor.lastrowid

                sql_item_compra = """
                    INSERT INTO item_compra (idproducto_servicio, idcompra, cantidad)
                    VALUES (%s, %s, %s)
                """
                valores_items = [
                    (item["idproducto_servicio"], id_compra, item["cantidad"])
                    for item in items_sanitizados
                ]
                cursor.executemany(sql_item_compra, valores_items)

                sql_actualizar_stock = """
                    UPDATE producto_servicio
                    SET cantidad_actual = cantidad_actual + %s
                    WHERE idproducto_servicio = %s AND tipo != 'servicio';
                """
                valores_stock = [
                    (item["cantidad"], item["idproducto_servicio"])
                    for item in items_sanitizados
                ]
                cursor.executemany(sql_actualizar_stock, valores_stock)

                conexion.commit()
                print(f"Compra #{id_compra} registrada exitosamente y stock actualizado.")
                return id_compra, True

        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al registrar la compra: {e}")
            return None, False

        finally:
            conexion.close()

    @staticmethod
    def obtener_compras_paginadas(
        busqueda=None,
        filtro_fecha="hoy",
        fecha_inicio=None,
        fecha_fin=None,
        estado=1,
        pagina=1,
        limite=20,
    ):
        """Lee el listado de compras aplicando filtros dinámicos, paginación
        y devuelve métricas acordes a la búsqueda realizada.
        """
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:

                # 1. Construcción dinámica de la cláusula WHERE y parámetros
                condiciones = []
                parametros = []

                # Filtro por estado (1 = Activo, 0 = Inactivo)
                if estado is not None:
                    condiciones.append("c.activo = %s")
                    parametros.append(estado)

                # Filtro por texto (Buscador por idcompra o nombre de proveedor)
                if busqueda and busqueda.strip():
                    condiciones.append("""(
                        CAST(c.idcompra AS CHAR) LIKE %s 
                        OR p.nombre LIKE %s
                    )""")
                    patron = f"%{busqueda.strip()}%"
                    parametros.extend([patron, patron])

                # Filtro por rango de fecha específico o predefinido
                if fecha_inicio and fecha_fin:
                    condiciones.append("c.fecha BETWEEN %s AND %s")
                    parametros.extend([fecha_inicio, fecha_fin])
                elif filtro_fecha == "hoy":
                    condiciones.append("c.fecha >= CURDATE()")
                elif filtro_fecha == "semana":
                    condiciones.append(
                        "c.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
                    )
                elif filtro_fecha == "mes":
                    condiciones.append(
                        "c.fecha >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
                    )
                elif filtro_fecha == "anio":
                    condiciones.append(
                        "c.fecha >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
                    )

                where_clause = (
                    (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
                )

                # 2. Obtener métricas agregadas (sincronizadas con los filtros)
                sql_totales = f"""
                    SELECT 
                        COUNT(c.idcompra) AS total_compras,
                        IFNULL(SUM(c.cantidad_total), 0) AS total_productos
                    FROM compra AS c
                    LEFT JOIN proveedor AS p ON c.idproveedor = p.idproveedor
                    {where_clause}
                """
                cursor.execute(sql_totales, parametros)
                res_totales = cursor.fetchone() or {}

                total_compras = res_totales.get("total_compras", 0)
                total_productos = int(res_totales.get("total_productos", 0))

                # Cálculo de paginación
                pagina = max(1, int(pagina))
                limite = max(1, int(limite))
                total_paginas = (
                    math.ceil(total_compras / limite) if total_compras > 0 else 1
                )
                pagina = min(pagina, total_paginas)
                offset = (pagina - 1) * limite

                # 3. Consulta de las compras paginadas
                sql_compras = f"""
                    SELECT 
                        c.idcompra,
                        c.fecha,
                        c.horas,
                        IFNULL(p.nombre, 'Sin Proveedor') AS proveedor,
                        (
                            SELECT GROUP_CONCAT(DISTINCT ps.tipo SEPARATOR ', ')
                            FROM item_compra AS ic
                            INNER JOIN producto_servicio AS ps ON ic.idproducto_servicio = ps.idproducto_servicio
                            WHERE ic.idcompra = c.idcompra
                        ) AS tipo,
                        IFNULL(c.cantidad_total, 0) AS total_productos,
                        c.activo AS estado
                    FROM compra AS c
                    LEFT JOIN proveedor AS p ON c.idproveedor = p.idproveedor
                    {where_clause}
                    ORDER BY c.fecha DESC, c.horas DESC, c.idcompra DESC
                    LIMIT %s OFFSET %s;
                """

                parametros_compras = parametros.copy()
                parametros_compras.extend([limite, offset])

                cursor.execute(sql_compras, parametros_compras)
                compras = cursor.fetchall()

                # Formatear objetos tipo date/datetime a string (Día/Mes/Año)
                for comp in compras:
                    if isinstance(comp.get("fecha"), (datetime, date)):
                        comp["fecha"] = comp["fecha"].strftime("%d/%m/%Y")
                    if comp.get("horas") is not None:
                        comp["horas"] = str(comp["horas"])

                return {
                    "compras": compras,
                    "paginacion": {
                        "pagina_actual": pagina,
                        "limite": limite,
                        "total_registros": total_compras,
                        "total_paginas": total_paginas,
                    },
                    "resumen": {
                        "total_compras": total_compras,
                        "total_productos": total_productos,
                    },
                    "Exito": True,
                }

        except pymysql.MySQLError as e:
            print(f"Error al consultar las compras: {e}")
            return {
                "compras": [],
                "paginacion": {
                    "pagina_actual": 1,
                    "limite": limite,
                    "total_registros": 0,
                    "total_paginas": 0,
                },
                "resumen": {
                    "total_compras": 0,
                    "total_productos": 0,
                },
                "Exito": False,
            }
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_id(id_compra):
        """Obtiene la cabecera de la orden de compra y el detalle de sus ítems."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql_cabecera = """
                    SELECT 
                        c.idcompra,
                        c.fecha,
                        c.horas,
                        IFNULL(p.nombre, 'Sin Proveedor') AS proveedor,
                        c.cantidad_total AS total_productos,
                        c.activo
                    FROM compra AS c
                    LEFT JOIN proveedor AS p ON c.idproveedor = p.idproveedor
                    WHERE c.idcompra = %s;
                """
                cursor.execute(sql_cabecera, (id_compra,))
                compra = cursor.fetchone()

                if not compra:
                    return [], [], False

                if isinstance(compra.get("fecha"), (datetime, date)):
                    compra["fecha"] = compra["fecha"].strftime("%d/%m/%Y")
                if compra.get("horas") is not None:
                    compra["horas"] = str(compra["horas"])

                sql_items = """
                    SELECT 
                        ic.iditem_compra,
                        ps.nombre AS producto_nombre,
                        ps.tipo AS producto_tipo,
                        ic.cantidad,
                        ic.precio_unitario,
                        (ic.cantidad * ic.precio_unitario) AS subtotal
                    FROM item_compra AS ic
                    INNER JOIN producto_servicio AS ps ON ic.idproducto_servicio = ps.idproducto_servicio
                    WHERE ic.idcompra = %s;
                """
                cursor.execute(sql_items, (id_compra,))
                items = cursor.fetchall()

                return compra, items, True

        except Exception as e:
            print(f"Error al obtener el detalle de la compra #{id_compra}: {e}")
            return [], [], False
        finally:
            conexion.close()

    @staticmethod
    def anular(id_compra):
        """Anula una compra y revierte el stock de los artículos que no son servicios."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT activo FROM compra WHERE idcompra = %s;", (id_compra,)
                )
                compra = cursor.fetchone()

                if not compra:
                    print(f"La compra ID {id_compra} no existe.")
                    return False

                if compra["activo"] == 0:
                    print(f"La compra ID {id_compra} ya se encuentra anulada.")
                    return False

                # Obtener ítems comprados para revertir el ingreso a stock
                sql_obtener_items = """
                    SELECT idproducto_servicio, cantidad 
                    FROM item_compra 
                    WHERE idcompra = %s;
                """
                cursor.execute(sql_obtener_items, (id_compra,))
                items = cursor.fetchall()

                # En una compra se sumó stock; al anular se resta del inventario
                sql_revertir_stock = """
                    UPDATE producto_servicio 
                    SET cantidad_actual = cantidad_actual - %s 
                    WHERE idproducto_servicio = %s AND tipo != 'servicio';
                """
                valores_stock = [
                    (item["cantidad"], item["idproducto_servicio"]) for item in items
                ]

                if valores_stock:
                    cursor.executemany(sql_revertir_stock, valores_stock)

                # Anulación lógica (activo = 0)
                sql_anular = "UPDATE compra SET activo = 0 WHERE idcompra = %s;"
                cursor.execute(sql_anular, (id_compra,))

            conexion.commit()
            print(f"Compra #{id_compra} anulada exitosamente y stock ajustado.")
            return True

        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al anular la compra ID {id_compra}: {e}")
            return False

        finally:
            conexion.close()
            
    @staticmethod
    def obtener_datos_inicio_compra():
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT p.idproducto_servicio, p.nombre, p.medidas, p.tipo, p.imagen_producto, p.cantidad_actual, p.cantidad_minima FROM producto_servicio AS p WHERE activo = 1 ORDER BY p.cantidad_actual ASC;")
                productos = cursor.fetchall()

                cursor.execute("SELECT DISTINCT tipo FROM producto_servicio WHERE activo = 1;")
                tipos = cursor.fetchall()

                cursor.execute("SELECT idproveedor, nombre, telefono, mail FROM proveedor WHERE activo = 1")
                proveedores = cursor.fetchall()

                return productos, tipos, proveedores, True
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al cargar los datos iniciales de compra: {e}")
            return [], [], [], False

        finally:
            conexion.close()