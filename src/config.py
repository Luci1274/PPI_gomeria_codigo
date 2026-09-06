import os
import pymysql
import cloudinary
from pathlib import Path
from dotenv import load_dotenv

Base_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=Base_dir / ".env")

class Config:
    SECRET_KEY = os.getenv("CLAVE_SECRETA", "clave_por_defecto_dev")

    RUTAS_PUBLICAS = [
        ruta.strip() for ruta in os.getenv("RUTAS_PUBLICAS", "").split(",") if ruta.strip()
    ]
    ROLES = [
        role.strip() for role in os.getenv("ROLES", "").split(",") if role.strip()
    ]

    # 2. Métodos de conexión
    @staticmethod
    def conectar_db():
        return pymysql.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            port=int(os.environ.get("DB_PORT", 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )

    @staticmethod
    def conectar_cloudinary():
        return cloudinary.config(
            cloud_name=os.environ.get("TU_CLOUD_NAME"),
            api_key=os.environ.get("TU_API_KEY"),
            api_secret=os.environ.get("TU_API_SECRET"),
            secure=True,
        )