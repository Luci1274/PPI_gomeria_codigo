import pymysql
from modulos.comandos_db.conexion import conectar_db

#--------------------------------------------------------------------------
# TABLA VENTA #
#--------------------------------------------------------------------------
def sql_registrar_venta_completa(id_cliente, id_empleado, descuento, iva, lista_items):
    """
    Registra la Venta, sus Ítems y descuenta el Stock en una sola transacción atómica.
    """
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            # 1. Calcular totales
            total_productos = sum(item['cantidad'] for item in lista_items)
            
            # 2. Insertar la cabecera de la venta
            sql_venta = """
                INSERT INTO venta (
                    idclientes, idempleados, descuento, iva, cantidad_total_productos, activa
                ) VALUES (%s, %s, %s, %s, %s, 1);
            """
            cursor.execute(sql_venta, (id_cliente, id_empleado, descuento, iva, total_productos))
            id_venta = cursor.lastrowid # Obtenemos el ID generado para la venta

            # 3. Preparar e insertar todos los ítems juntos
            sql_items = """
                INSERT INTO item_venta (
                    idventa, idproducto_servicio, precio_unitario, cantidad
                ) VALUES (%s, %s, %s, %s);
            """
            valores_items = [
                (id_venta, item['idproducto_servicio'], item['precio_unitario'], item['cantidad'])
                for item in lista_items
            ]
            cursor.executemany(sql_items, valores_items)

            # 4. Descontar stock de los productos vendidos
            sql_stock = """
                UPDATE producto_servicio 
                SET cantidad_actual = cantidad_actual - %s 
                WHERE idproducto_servicio = %s AND tipo = 'producto';
            """
            valores_stock = [
                (item['cantidad'], item['idproducto_servicio'])
                for item in lista_items
            ]
            cursor.executemany(sql_stock, valores_stock)

        # Si todo salió bien, guardamos definitivamente en la base de datos
        conexion.commit()
        print(f"Venta #{id_venta} procesada exitosamente.")
        return id_venta

    except pymysql.MySQLError as e:
        # Si falla algo en CUALQUIERA de los 4 pasos, se deshacen todos los cambios
        conexion.rollback()
        print(f"Error al procesar la venta: {e}")
        return None

    finally:
        conexion.close()
#--------------------------------------------------------------------------
def sql_leer_ventas(busqueda=None, filtro_fecha="hoy"):
    """
    Lee las ventas aplicando filtros opcionales de búsqueda y fecha.
    """
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    v.idventas,
                    v.numero_factura,
                    v.fecha_emision_factura,
                    CONCAT(IFNULL(c.nombre, 'Consumidor'), ' ', IFNULL(c.apellido, 'Final')) AS cliente,
                    v.cantidad_total_productos,
                    IFNULL(SUM(iv.precio_unitario * iv.cantidad), 0) AS total_precio
                FROM venta AS v
                LEFT JOIN cliente AS c ON v.idclientes = c.idclientes
                LEFT JOIN item_venta AS iv ON v.idventas = iv.ventas_idventas
                WHERE v.activa = 1
            """
            parametros = []

            # 1. Filtro por texto (Nº de venta, Nº de factura o Nombre/Apellido del cliente)
            if busqueda and busqueda.strip():
                sql += """ AND (
                    v.idventas LIKE %s 
                    OR v.numero_factura LIKE %s 
                    OR c.nombre LIKE %s 
                    OR c.apellido LIKE %s
                    OR CONCAT(c.nombre, ' ', c.apellido) LIKE %s
                )"""
                patron = f"%{busqueda.strip()}%"
                parametros.extend([patron, patron, patron, patron, patron])

            # 2. Filtro por rango de fecha
            if filtro_fecha == 'hoy':
                sql += " AND DATE(v.fecha_emision_factura) = CURDATE()"
            elif filtro_fecha == 'semana':
                sql += " AND v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            elif filtro_fecha == 'mes':
                sql += " AND v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
            elif filtro_fecha == 'anio':
                sql += " AND v.fecha_emision_factura >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"

            # Agrupación y orden descendente (las más recientes primero)
            sql += " GROUP BY v.idventas ORDER BY v.fecha_emision_factura DESC;"

            cursor.execute(sql, parametros)
            return cursor.fetchall()

    except pymysql.MySQLError as e:
        print(f"Error al consultar las ventas: {e}")
        return []

    finally:
        conexion.close()

import pymysql
from modulos.comandos_db.conexion import conectar_db

#----------------------------------------------------------------------------
def sql_anular_venta(id_venta):
    """
    Realiza la anulación lógica de una venta (activa = 0)
    y devuelve la cantidad de productos vendidos al stock de producto_servicio.
    """
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            # 1. Verificar si la venta existe y está activa actualmente
            cursor.execute("SELECT activa FROM venta WHERE idventa = %s;", (id_venta,))
            venta = cursor.fetchone()

            if not venta:
                print(f"La venta ID {id_venta} no existe.")
                return False

            if venta['activa'] == 0:
                print(f"La venta ID {id_venta} ya se encuentra anulada.")
                return False

            # 2. Obtener los ítems asociados a esta venta para saber qué devolver al stock
            # Nota: Usamos idproducto_servido conforme a la columna de tu tabla
            sql_obtener_items = """
                SELECT idproducto_servido, cantidad 
                FROM item_venta 
                WHERE idventa = %s;
            """
            cursor.execute(sql_obtener_items, (id_venta,))
            items = cursor.fetchall()

            # 3. Sumar las cantidades vendidas de vuelta al stock de producto_servicio
            sql_restituir_stock = """
                UPDATE producto_servicio 
                SET cantidad_actual = cantidad_actual + %s 
                WHERE idproducto_servicio = %s AND tipo = 'producto';
            """
            valores_stock = [
                (item['cantidad'], item['idproducto_servido']) 
                for item in items
            ]
            
            if valores_stock:
                cursor.executemany(sql_restituir_stock, valores_stock)

            # 4. Cambiar el estado de la venta a inactiva (activa = 0)
            sql_anular = "UPDATE venta SET activa = 0 WHERE idventa = %s;"
            cursor.execute(sql_anular, (id_venta,))

        # Si todos los pasos fueron exitosos, confirmamos los cambios en la BD
        conexion.commit()
        print(f"Venta #{id_venta} anulada exitosamente y stock restituido.")
        return True

    except pymysql.MySQLError as e:
        # En caso de error, deshacemos todos los pasos para no alterar el stock por error
        conexion.rollback()
        print(f"Error al anular la venta ID {id_venta}: {e}")
        return False

    finally:
        conexion.close()