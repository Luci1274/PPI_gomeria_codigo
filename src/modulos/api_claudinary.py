import cloudinary
import cloudinary.uploader
from config import Config

# 1. Se agregan los paréntesis () para ejecutar la configuración al importar el módulo
Config.conectar_cloudinary()

def subir_imagen(imagen):
    try:
        # 2. Pasamos 'imagen' directamente (Cloudinary soporta objetos FileStorage de Flask)
        respuesta = cloudinary.uploader.upload(
            imagen,
            folder="gomeria",
            transformation=[
                {"width": 600, "height": 600, "crop": "limit"},
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        
        # 3. Retornamos solo la URL HTTPS segura para guardar en la base de datos
        return respuesta.get("secure_url")

    except Exception as e:
        print(f"Error al subir la imagen a Cloudinary: {e}")
        return None