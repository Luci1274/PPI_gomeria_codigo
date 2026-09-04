import pymysql
from config import Config

#----------------------------------------------------------------------------
def sql_crear_proveedor(nombre, cuit, direccion, mail, ciudad, telefono):
    """Crea un nuevo proveedor en la base de datos."""
    sql = """INSERT INTO proveedor (nombre, cuit, direccion, mail, ciudad, telefono, activo) VALUES (%s, %s, %s, %s, %s, %s, 1)"""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            valores = (nombre, cuit, direccion, mail, ciudad, telefono)
            cursor.execute(sql, valores)
        conexion.commit()
        id_nuevo_proveedor = cursor.lastrowid
            
        print("Proveedor guardado correctamente")
        return id_nuevo_proveedor
    
    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al crear proveedor: {e}")
        return None
    
    finally:
        conexion.close()

#----------------------------------------------------------------------------

def sql_leer_proveedores(busqueda=None):
    """ Lee los proveedores activos de la base de datos, aplicando un filtro opcional de búsqueda.
    """
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT idproveedor, nombre, cuit, direccion, mail, ciudad, telefono FROM proveedor WHERE activo = 1"
            if busqueda and busqueda.strip():
                sql += " AND (nombre LIKE %s OR cuit LIKE %s OR direccion LIKE %s OR mail LIKE %s OR ciudad LIKE %s OR telefono LIKE %s)"
                patron = f"%{busqueda.strip()}%"
                parametros = [patron] * 6
            cursor.execute(sql, parametros)
            proveedores = cursor.fetchall()
    except Exception as e:
        print(f"Error al leer proveedores: {e}")
        proveedores = []
    finally:
        conexion.close()
    return proveedores
#----------------------------------------------------------------------------
def sql_leer_proveedor(id):
    """Busca el proveedor por el id y lo devuelve"""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT idproveedor, nombre, cuit, direccion, mail, ciudad, telefono FROM proveedor WHERE idproveedor = %s"
            cursor.execute(sql, (id,))
            proveedor = cursor.fetchone()
    except Exception as e:
        print(f"Error al leer proveedor: {e}")
        proveedor = None
    finally:
        conexion.close()
    return proveedor

#----------------------------------------------------------------------------
def sql_modificar_proveedor(id, nombre, cuit, direccion, mail, ciudad, telefono):
    """Modifica los datos de un proveedor existente en la base de datos."""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = """
                UPDATE proveedor
                SET nombre = %s,
                    cuit = %s,
                    direccion = %s,
                    mail = %s,
                    ciudad = %s,
                    telefono = %s
                WHERE idproveedor = %s
            """
            cursor.execute(sql, (nombre, cuit, direccion, mail, ciudad, telefono, id))
            conexion.commit()
            return True
    except Exception as e:
        print(f"Error al modificar proveedor: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()
        
#----------------------------------------------------------------------------
def sql_eliminar_proveedor(id):
    """Elimina un proveedor de la base de datos de forma logica"""
    conexion = Config.conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = "UPDATE proveedor SET activo = 0 WHERE idproveedor = %s"
            cursor.execute(sql, (id,))
            conexion.commit()
            return True
    except Exception as e:
        print(f"Error al eliminar proveedor: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()