import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
from dotenv import load_dotenv

#Configuración       
cloudinary.config(
cloud_name= os.environ.get("CLOUD_NAME"),
api_key=os.environ.get("API_KEY"),
api_secret=os.environ.get("API_SECRET"),
secure=True,
)

def subir_imagen(imagen_producto, carpeta="productos"):
    """Recibe el archivo subido desde el formulario en HTML"""
    """Lo sube a claudinary"""
    """Devuelve la url"""
    try:
        # Cloudinary acepta directamente el objeto file que viene de Flask (request.files['foto'])
        resultado = cloudinary.uploader.upload(
            imagen_producto,
            folder=carpeta,  # Organiza las imágenes dentro de una carpeta en Cloudinary
            resource_type="image",
        )

        # Retornamos la URL segura que guardaremos en la base de datos MySQL
        return resultado.get("secure_url")

    except Exception as e:
        print(f"Error al subir imagen a Cloudinary: {e}")
        return None
    
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# 1. Configuración de Cloudinary
# Reemplaza con tus credenciales o asegúrate de cargarlas desde variables de entorno
cloudinary.config(
    cloud_name="TU_CLOUD_NAME",
    api_key="TU_API_KEY",
    api_secret="TU_API_SECRET",
    secure=True,
)


def subir_imagen(archivo_flask, carpeta="productos"):
    """Recibe el archivo subido desde el formulario HTML en Flask (FileStorage)

    y lo sube a Cloudinary.

    Retorna:
        str: La URL HTTPS (secure_url) generada por Cloudinary para guardar en MySQL.
    """
    try:
        # Cloudinary acepta directamente el objeto file que viene de Flask (request.files['foto'])
        resultado = cloudinary.uploader.upload(
            archivo_flask,
            folder=carpeta,  # Organiza las imágenes dentro de una carpeta en Cloudinary
            resource_type="image",
        )

        # Retornamos la URL segura que guardaremos en la base de datos MySQL
        return resultado.get("secure_url")

    except Exception as e:
        print(f"Error al subir imagen a Cloudinary: {e}")
        return None


def obtener_urls_optimizadas(
    lista_urls, width=500, height=500, crop="limit", quality="auto", format="auto"
):
    """Recibe una lista de URLs guardadas en MySQL (o una sola URL) y aplica
    transformaciones automáticas de Cloudinary (optimización de peso, formato webp,
    redimensión).
    Retorna:
        list: Lista con las URLs optimizadas listas para pasar al HTML/Jinja2.
    """
    urls_optimizadas = []

    for url in lista_urls:
        if not url:
            continue

        # Extraemos el 'public_id' de la URL de Cloudinary para aplicarle transformaciones
        # Ejemplo URL: https://res.cloudinary.com/demo/image/upload/v123456/productos/foto.jpg
        # Extrae: "productos/foto"
        try:
            # Dividimos la URL para obtener la ruta del recurso
            partes = url.split("/upload/")
            if len(partes) > 1:
                # Quitamos la versión (v123456/) si existe y la extensión (.jpg/.png)
                ruta_recurso = partes[1].split("/", 1)[-1]  # Omitir versión v123...
                public_id = ruta_recurso.rsplit(".", 1)[0]  # Omitir extensión

                # Generamos la nueva URL optimizada
                url_opt, _ = cloudinary_url(
                    public_id,
                    width=width,
                    height=height,
                    crop=crop,
                    fetch_format=format,  # Convierte automáticamente a WebP/AVIF según el navegador
                    quality=quality,  # Comprime la imagen sin pérdida visible de calidad
                )
                urls_optimizadas.append(url_opt)
            else:
                # Si por alguna razón no es una URL estándar de Cloudinary, dejamos la original
                urls_optimizadas.append(url)
        except Exception:
            urls_optimizadas.append(url)

    return urls_optimizadas