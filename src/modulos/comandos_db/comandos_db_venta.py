import pymysql
from modulos.comandos_db.conexion import conectar_db

#------------------------------------------------------------------------
# TABLA VENTA
#------------------------------------------------------------------------
def sql_registrar_venta_completa(
    id_cliente,
    id_empleado,
    lista_items,
    numero_factura=None,
    iva=21,
    descuento=0,
    precio_total=0.0,
    total_productos=0,
):
    """Registra la Venta, sus Ítems y descuenta el Stock en una sola transacción atómica."""
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            # 1. Insertar la cabecera de la venta
            sql_venta = """
                INSERT INTO venta (
                    idcliente, idempleado, descuento, iva, cantidad_total_productos, precio_total, numero_factura, fecha_emision_factura, activa
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), 1);
            """
            cursor.execute(
                sql_venta,
                (
                    id_cliente,
                    id_empleado,
                    descuento,
                    iva,
                    total_productos,
                    precio_total,
                    numero_factura,
                ),
            )
            id_venta = cursor.lastrowid

            # 2. Insertar los ítems asociados
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

            # 3. Descontar stock únicamente para ítems de tipo 'producto'
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

    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al procesar la venta: {e}")
        return None

    finally:
        conexion.close()


#------------------------------------------------------------------------
def sql_leer_ventas(busqueda=None, filtro_fecha="hoy"):
    """Lee el listado general de ventas aplicando filtros opcionales de búsqueda y fecha."""
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    v.idventa,
                    v.numero_factura,
                    v.fecha_emision_factura,
                    CONCAT(IFNULL(c.nombre, 'Consumidor'), ' ', IFNULL(c.apellido, 'Final')) AS cliente,
                    v.cantidad_total_productos,
                    v.precio_total
                FROM venta AS v
                LEFT JOIN cliente AS c ON v.idcliente = c.idcliente
                WHERE v.activa = 1
            """
            parametros = []

            if busqueda and busqueda.strip():
                sql += """ AND (
                    v.idventa LIKE %s 
                    OR v.numero_factura LIKE %s 
                    OR c.nombre LIKE %s 
                    OR c.apellido LIKE %s
                    OR CONCAT(c.nombre, ' ', c.apellido) LIKE %s
                )"""
                patron = f"%{busqueda.strip()}%"
                parametros.extend([patron, patron, patron, patron, patron])

            if filtro_fecha == "hoy":
                sql += " AND DATE(v.fecha_emision_factura) = CURDATE()"
            elif filtro_fecha == "semana":
                sql += " AND v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            elif filtro_fecha == "mes":
                sql += " AND v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
            elif filtro_fecha == "anio":
                sql += " AND v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"

            sql += " ORDER BY v.fecha_emision_factura DESC;"

            cursor.execute(sql, parametros)
            return cursor.fetchall()

    except pymysql.MySQLError as e:
        print(f"Error al consultar las ventas: {e}")
        return []

    finally:
        conexion.close()


#------------------------------------------------------------------------
def sql_leer_venta(id_venta):
    """Obtiene la cabecera de la venta y la lista de sus productos para la pantalla de detalle."""
    conexion = conectar_db()
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
                    iv.iditem_venta,
                    iv.cantidad,
                    iv.precio_unitario,
                    (iv.cantidad * iv.precio_unitario) AS subtotal,
                    ps.nombre AS producto_nombre,
                    ps.imagen_url
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


#------------------------------------------------------------------------

def sql_anular_venta(id_venta):
    """Anula de forma lógica una venta y reintegra las cantidades al stock de productos."""
    conexion = conectar_db()
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