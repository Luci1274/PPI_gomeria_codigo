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