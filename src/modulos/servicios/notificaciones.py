import ssl
import smtplib
import random
from email.mime.text import MIMEText
from twilio.rest import Client
from config import Config

Config = Config()
GMAIL_USER = Config.obtener_credenciales_gmail()["user"]
GMAIL_PASS = Config.obtener_credenciales_gmail()["pass"]

TWILIO_SID = Config.obtener_credenciales_twilio()["sid"]
TWILIO_TOKEN = Config.obtener_credenciales_twilio()["token"]
TWILIO_PHONE_NUMBER = Config.obtener_credenciales_twilio()["whatsapp_number"]

def generar_token():
    """Genera un código numérico aleatorio de 6 dígitos."""
    return str(random.randint(100000, 999999))

def enviar_correo(destinatario, token):
    msg = MIMEText(f"Tu código de verificación para restablecer tu contraseña es: {token}\n\nEste código expira en 15 minutos.")
    msg['Subject'] = "Código de Recuperación de Contraseña"
    msg['From'] = GMAIL_USER
    msg['To'] = destinatario

    # Contexto SSL explícito y timeouts para evitar el 'Connection unexpectedly closed'
    context = ssl.create_default_context()
    with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)

def enviar_sms(numero_telefono, token):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    num_limpio = numero_telefono.strip()
    
    if not num_limpio.startswith("+"):
        num_limpio = f"+{num_limpio}"

    client.messages.create(
        from_=TWILIO_PHONE_NUMBER,
        body=f"Tu código de recuperación es: {token}. Válido por 15 minutos.",
        to=num_limpio
    )

def enviar_token_recuperacion(contacto, token):
    """Detecta si el contacto es email o teléfono e intenta el envío."""
    is_email = "@" in contacto
    
    try:
        if is_email:
            enviar_correo(contacto, token)
            print(f"[OK] Correo enviado exitosamente a {contacto}")
        else:
            enviar_sms(contacto, token)
            print(f"[OK] SMS enviado exitosamente a {contacto}")
    except Exception as e:
        # Imprime el token en la terminal de Flask para poder continuar las pruebas locales
        print("\n=======================================================")
        print(f" [MODO DEV] TOKEN GENERADO PARA {contacto}: {token}")
        print(f" Detalle del error de envío: {e}")
        print("=======================================================\n")
        
        # Opcional: Descomenta la siguiente línea si quieres que falle la API en producción cuando falle el servicio externo
        # raise e