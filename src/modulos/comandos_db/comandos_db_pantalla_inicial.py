from config import Config
import pymysql

def contar_cantidad_productos():
    return "SELECT COUNT(idproducto_servicio) AS total FROM producto_servicio WHERE activo = 1"

def contar_total_clientes():
    return "SELECT COUNT(idcliente) AS total FROM cliente WHERE activo = 1"

def contar_ventas_dia():
    return "SELECT COUNT(idventa) AS total FROM venta WHERE DATE(fecha_emision_factura) = CURDATE() AND activa = 1"

def obtener_ultimas_ventas():
    return """
        SELECT c.nombre, c.apellido, v.precio_total, hpc.forma_pago, v.estado 
        FROM venta AS v 
        JOIN cliente AS c ON v.idcliente = c.idcliente 
        LEFT JOIN historial_pago_cliente AS hpc ON v.idventa = hpc.idventa 
        WHERE v.activa = 1
        ORDER BY v.idventa DESC
        LIMIT 5
    """

def obtener_stock_bajo():
    return "SELECT idproducto_servicio, nombre, cantidad_actual FROM producto_servicio WHERE activo = 1 AND cantidad_actual < cantidad_minima;"

def mostrar():
    conexion = Config.conectar_db()
    try:
        
        with conexion.cursor() as cursor:
            cursor.execute(contar_cantidad_productos())
            res_prod = cursor.fetchone()
            total_productos = res_prod['total'] if res_prod else 0

            cursor.execute(contar_total_clientes())
            res_cli = cursor.fetchone()
            total_clientes = res_cli['total'] if res_cli else 0

            cursor.execute(contar_ventas_dia())
            res_ventas = cursor.fetchone()
            ventas_dia = res_ventas['total'] if res_ventas else 0

            cursor.execute(obtener_ultimas_ventas())
            ultimas_ventas = cursor.fetchall()

            cursor.execute(obtener_stock_bajo())
            productos_bajos = cursor.fetchall()

            return total_productos, total_clientes, ventas_dia, ultimas_ventas, productos_bajos, True

    except pymysql.MySQLError as e:
        print(f"Error al ejecutar la consulta: {e}")
        return 0, 0, 0, [], [], False

    finally:
        conexion.close()