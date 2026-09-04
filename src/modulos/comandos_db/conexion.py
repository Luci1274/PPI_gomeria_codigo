import pymysql
from config import Config

def probar_conexion():
    try:
        conexion = Config.conectar_db()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT 1")
            resultado = cursor.fetchone()
            if resultado:
                print("Conexión a la base de datos exitosa.")
                return True
            else:
                print("Conexión a la base de datos fallida.")
                return False
    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return False
    finally:
        conexion.close()