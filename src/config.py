import os
import pymysql
import cloudinary
from pathlib import Path
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

Base_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=Base_dir / ".env")

# Pool de conexiones activo desde el arranque de la app
db_pool = PooledDB(
    creator=pymysql,
    mincached=2,        # Mantiene al menos 2 conexiones vivas y autenticadas con Aiven
    maxconnections=10,  # Límite máximo de conexiones según el tráfico
    blocking=True,      # Espera si todas las conexiones están ocupadas
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME"),
    port=int(os.environ.get("DB_PORT", 3306)),
    cursorclass=pymysql.cursors.DictCursor
)

class Config:
    SECRET_KEY = os.getenv("CLAVE_SECRETA", "clave_por_defecto_dev")

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
            "/api/registrarse",
            "/api/recuperar/solicitar",
            "/api/recuperar/validar_token",
            "/api/recuperar/restablecer"
        ]

    _roles_env = os.getenv("ROLES")
    if _roles_env:
        ROLES = [r.strip() for r in _roles_env.split(",") if r.strip()]
    else:
        ROLES = ["DEV", "AD", "EM"]

    # 2. Métodos de conexión
    @staticmethod
    def conectar_db():
        # Entrega una conexión lista del pool
        return db_pool.connection()

    @staticmethod
    def conectar_cloudinary():
        return cloudinary.config(
            cloud_name=os.environ.get("TU_CLOUD_NAME"),
            api_key=os.environ.get("TU_API_KEY"),
            api_secret=os.environ.get("TU_API_SECRET"),
            secure=True,
        )
    
    @staticmethod
    def obtener_credenciales_twilio():
        from twilio.rest import Client
        return {
            "sid": os.environ.get("TWILIO_SID"),
            "token": os.environ.get("TWILIO_TOKEN"),
            "whatsapp_number": os.environ.get("TWILIO_WHATSAPP_NUMBER")
        }
    
    @staticmethod
    def obtener_credenciales_gmail():
        return {
            "user": os.environ.get("GMAIL_USER"),
            "pass": os.environ.get("GMAIL_PASS")
        }