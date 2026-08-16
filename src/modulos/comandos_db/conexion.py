import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


#configuración de la conexión
def conectar_db():
    return pymysql.connect(
        host = os.environ.get("DB_HOST"),
        user = os.environ.get("DB_USER"),
        password = os.environ.get("DB_PASSWORD"),
        database = os.environ.get("DB_NAME"),
        port = int(os.environ.get("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )
    
def probar_conexion():
    try:
        conexion = conectar_db()
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