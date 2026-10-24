from config import Config
import random
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

# Configuración de credenciales
Config = Config()
GMAIL_USER = Config.obtener_credenciales_gmail()["user"]
GMAIL_PASS = Config.obtener_credenciales_gmail()["pass"]
TWILIO_SID = Config.obtener_credenciales_twilio()["sid"]
TWILIO_TOKEN = Config.obtener_credenciales_twilio()["token"]
TWILIO_WHATSAPP_NUMBER = Config.obtener_credenciales_twilio()["whatsapp_number"]

def generar_token():
    """Genera un código numérico aleatorio de 6 dígitos."""
    return str(random.randint(100000, 999999))

def enviar_correo(destinatario, token):
    msg = MIMEText(f"Tu código de verificación para restablecer tu contraseña es: {token}\n\nEste código expira en 15 minutos.")
    msg['Subject'] = "Código de Recuperación de Contraseña"
    msg['From'] = GMAIL_USER
    msg['To'] = destinatario

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)

def enviar_whatsapp(numero_telefono, token):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=f"Tu código de recuperación es: *{token}*\nVálido por 15 minutos.",
        to=f"whatsapp:{numero_telefono}"
    )

def enviar_token_recuperacion(contacto, token):
    """Detecta si el contacto es email o teléfono y envía el token."""
    if "@" in contacto:
        enviar_correo(contacto, token)
    else:
        enviar_whatsapp(contacto, token)