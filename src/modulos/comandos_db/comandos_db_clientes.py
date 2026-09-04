import pymysql
from config import Config

#----------------------------------------------------------------------------
def sql_crear_cliente(nombre, apellido, cuit, numero_tel, mail, plazo_de_pago, deuda = "no", activo = 1):
    """Crea un nuevo cliente en la base de datos"""
    sql = """INSERT INTO clientes (nombre, apellido, cuit, numero_tel, mail, plazo_de_pago, deuda, activo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            valores = (nombre, apellido, cuit, numero_tel, mail, plazo_de_pago, deuda, activo)
            cursor.execute(sql, valores)
        conexion.commit()
        id_nuevo_cliente = cursor.lastrowid
            
        """Esto es para nosotros"""
        print("Cliente guardado correctamnete")
        return id_nuevo_cliente
    
    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al crear cliente: {e}")
        return None
    
    finally:
        conexion.close()
#----------------------------------------------------------------------------
def sql_leer_clientes(busqueda=None):
    """Lee los clientes activos de la base de datos."""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT * FROM cliente WHERE activo = 1"
            
            parametros = []
            
            if busqueda:
                sql += " AND (nombre LIKE %s OR apellido LIKE %s OR cuit LIKE %s)"
                parametros.extend([f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"])
            
            cursor.execute(sql, parametros)
            listado_clientes = cursor.fetchall()
            if len(listado_clientes) == 0:
                return []

            else:
                return listado_clientes
            
    except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al leer clientes: {e}")
            return []

    finally:
        conexion.close()
#----------------------------------------------------------------------------
def sql_leer_cliente(id):
    """Lee un cliente específico de la base de datos por su ID."""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT * FROM clientes WHERE id = %s AND activo = 1"
            cursor.execute(sql, (id,))
            cliente = cursor.fetchone()
            return cliente
        
    except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al leer cliente: {e}")
            return None

    finally:
        conexion.close()
#----------------------------------------------------------------------------
def sql_actualizar_cliente(id, nombre, apellido, cuit, numero_tel, mail, plazo_de_pago, deuda):
    """Actualiza un cliente existente en la base de datos."""
    sql = """UPDATE clientes SET nombre = %s, apellido = %s, cuit = %s, numero_tel = %s, mail = %s, plazo_de_pago = %s, deuda = %s WHERE id = %s"""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            valores = (nombre, apellido, cuit, numero_tel, mail, plazo_de_pago, deuda, id)
            cursor.execute(sql, valores)
        conexion.commit()
        print("Cliente actualizado correctamente")
        return True
    
    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al actualizar cliente: {e}")
        return False
    
    finally:
        conexion.close()
#----------------------------------------------------------------------------
def sql_eliminar_cliente(id):
    """Elimina un cliente de la base de datos (eliminación lógica)."""
    sql = "UPDATE clientes SET activo = 0 WHERE id = %s"
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, (id,))
        conexion.commit()
        print("Cliente eliminado correctamente")
        return True
    
    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al eliminar cliente: {e}")
        return False
    
    finally:
        conexion.close()