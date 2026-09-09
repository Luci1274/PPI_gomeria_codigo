import os
import pymysql
import cloudinary
from pathlib import Path
from dotenv import load_dotenv

Base_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=Base_dir / ".env")

class Config:
    SECRET_KEY = os.getenv("CLAVE_SECRETA", "clave_por_defecto_dev")

    # Si os.getenv devuelve None o "", usamos una lista de respaldo predeterminada
    _rutas_env = os.getenv("RUTAS_PUBLICAS")
    if _rutas_env:
        RUTAS_PUBLICAS = [r.strip() for r in _rutas_env.split(",") if r.strip()]
    else:
        RUTAS_PUBLICAS = [
            "iniciar_sesion", 
            "registrarse", 
            "api_iniciar_sesion", 
            "api_registrarse", 
            "/iniciar_sesion", 
            "/registrarse", 
            "/api/iniciar_sesion", 
            "/api/registrarse"
        ]

    _roles_env = os.getenv("ROLES")
    if _roles_env:
        ROLES = [r.strip() for r in _roles_env.split(",") if r.strip()]
    else:
        ROLES = ["DEV", "AD", "EM"]

    # 2. Métodos de conexión
    @staticmethod
    def conectar_db():
        try:
            return pymysql.connect(
                host=os.environ.get("DB_HOST"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                database=os.environ.get("DB_NAME"),
                port=int(os.environ.get("DB_PORT", 3306)),
                connect_timeout=3,
                cursorclass=pymysql.cursors.DictCursor
            )
        except:
            return pymysql.connect(
                host="localhost",
                user="luci",
                password="1274",
                database="gomeria",
                port=3306,
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