import cloudinary
import cloudinary.uploader
from config import Config

Config.conectar_cloudinary()

def subir_imagen(imagen):
    try:
        respuesta = cloudinary.uploader.upload(
            imagen,
            folder="gomeria",
            transformation=[
                {
                    "width": 600, 
                    "height": 600, 
                    "crop": "fill", 
                    "gravity": "auto"
                },
                {"quality": "auto", "fetch_format": "auto", "flags": "strip_profile"}
            ]
        )
        
        return respuesta.get("secure_url")

    except Exception as e:
        print(f"Error al subir la imagen a Cloudinary: {e}")
        return None