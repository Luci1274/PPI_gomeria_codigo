import pymysql
import os
from dotenv import load_dotenv
from pathlib import Path
import cloudinary


Base_dir = Path(__file__).resolve().parent

load_dotenv(dotenv_path=Base_dir / ".env")

#configuración de la conexión
class Config:
    
    def conectar_db():
        return pymysql.connect(
            host = os.environ.get("DB_HOST"),
            user = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASSWORD"),
            database = os.environ.get("DB_NAME"),
            port = int(os.environ.get("DB_PORT", 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )
        
    def conectar_cloudinary():
        return cloudinary.config(
            cloud_name=os.environ.get("TU_CLOUD_NAME"),
            api_key=os.environ.get("TU_API_KEY"),
            api_secret=os.environ.get("TU_API_SECRET"),
            secure=True,
        )
    