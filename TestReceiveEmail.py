from flask import Flask
from flask_apscheduler import APScheduler
import paramiko
import time
import smtplib
import email
import imaplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import re
import pygetwindow as gw
from PIL import Image, ImageDraw, ImageFont
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from smtplib import SMTP

# Configuración de la aplicación en Azure AD
client_id = "6b528cdf-48fa-44ca-bddc-bb92915df304"
client_secret = "DwF8Q~cJG8E.Nd.5kEEzOgUQhtF_Dm~TvQbftaFQ"
tenant_id = "898b2aab-fa1b-4bd1-ae98-9923fff34e31"

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True

# Inicializar app flask
app = Flask(__name__)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()
# Definir la ruta local para guardar la captura de pantalla
local_path = f"screenshots/local_screenshot_{time.time()}.png"

def sendEmail(destinatario, asunto, body):

    # Configura los detalles del correo
    remitente = "cacevedo@acdata.cl"  # Cambia por tu correo de dominio propio
    password = "ljfmfgmdxfcqngqk"  # Cambia por tu contraseña  zghpsnvpplzkjhjj BotReporteCATO

    destinatarios = [destinatario]
    subject = asunto
    cuerpo = body

    # Configura el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = subject
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Configura el servidor SMTP de Gmail
    servidor_smtp = "smtp.office365.com"
    #smtp-mail.outlook.com
    #smtp.office365.com
    #smtp.gmail.com

    puerto_smtp = 587

    # Crea una conexión al servidor SMTP
    sesion_smtp = smtplib.SMTP(servidor_smtp, puerto_smtp)
    sesion_smtp.starttls()
    
    try:
        # Inicia sesión en el servidor
        sesion_smtp.login(remitente, password)

        # Envía el mensaje
        sesion_smtp.sendmail(remitente, destinatarios, mensaje.as_string())
        print("Correo enviado con éxito")

        # Retorna True indicando que el correo fue enviado correctamente
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de autenticación: {e}")
        # Retorna False indicando que hubo un error al enviar el correo
        return False
    finally:
        # Cierra la conexión
        sesion_smtp.quit()

def receiveEmail(instructions):
    
    # Configuración de acceso al correo electrónico
    email_user = "cacevedo@acdata.cl"
    email_password = "ljfmfgmdxfcqngqk"
    mail = imaplib.IMAP4_SSL("outlook.office365.com")
    #outlook.office365.com
    mail.login(email_user, email_password)
    mail.select("inbox")
    print("Validacion correcta !!!")
    # Buscar mensajes no leídos
    status, messages = mail.search(None, "(UNSEEN)")

    for mail_id in messages[0].split():
        _, msg_data = mail.fetch(mail_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Analizar el cuerpo del mensaje en busca de instrucciones
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8")

                    # Buscar cualquier instrucción de la lista
                    for instruction in instructions:
                        if re.search(instruction, body, re.IGNORECASE):
                            # Ejecutar la acción correspondiente aquí
                            print(f"Instrucción recibida: {instruction.lower()}")

                            message_lower = instruction.lower()

                            if message_lower == "reiniciar tuneles":

                                subjectMessage = "Confirmación de Reinicio del Tunnel de Acceso"
                                confirmation_text = "El tunnel de acceso ha sido reiniciado exitosamente."
                                sendEmail(msg["From"], subjectMessage, confirmation_text)

                            elif message_lower == "actualizar estado":

                                subjectMessage = "Confirmación de actualizacion del estado del Tunnel de Acceso"
                                confirmation_text = "El tunnel de acceso ha sido actualizado exitosamente."
                                sendEmail(msg["From"], subjectMessage, confirmation_text)

                            elif message_lower == "consulta estado":

                                subjectMessage = "Confirmación de actualizacion del estado del Tunnel de Acceso"
                                confirmation_text = "El tunnel de acceso ha sido actualizado exitosamente."
                                sendEmail(msg["From"], subjectMessage, confirmation_text)

                            # Salir del bucle cuando se encuentra una instrucción válida
                            break
                    else:
                        # Si no se encuentra ninguna instrucción válida
                        subjectMessage = f'No se reconoce o no se indico la instruccion: {instructions}'
                        confirmation_text = "No se recibió ninguna instrucción válida, favor indicar instrucción en el cuerpo del mensaje y enviar nuevamente"
                        sendEmail(msg["From"], subjectMessage, confirmation_text)

    # Cerrar conexión al servidor IMAP
    mail.logout()

def receiveEmailWrapper():
    print("Tarea ejecutada")
    receiveEmail(["Reiniciar tuneles", "Actualizar estado", "Consulta estado"])  # Puedes añadir más instrucciones según sea necesario

scheduler.add_job(id='1',func=receiveEmailWrapper,trigger='interval', minutes=0.1)

scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run()