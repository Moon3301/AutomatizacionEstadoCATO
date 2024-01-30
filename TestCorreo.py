from flask import Flask
from flask_apscheduler import APScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pygetwindow as gw

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True

# Inicializar app flask
app = Flask(__name__)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()

def sendEmail():
    # Configura los detalles del correo
    remitente = "cacevedo@acdata.cl"  # Cambia por tu correo de dominio propio
    #raziel203619@gmail.com
    #omxr msoe idwe ccvo
    password = "ljfmfgmdxfcqngqk"  # Cambia por tu contraseña ljfmfgmdxfcqngqk
    destinatarios = ['fynsabottest@gmail.com']
    asunto = 'Test Bot fynsa'
    cuerpo = 'Se adjunta captura de pantalla estado servicio.'

    # Configura el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto
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

scheduler.add_job(id='1',func=sendEmail,trigger='cron', hour=15, minute=41)
scheduler.add_job(id='2',func=sendEmail,trigger='cron', hour=14, minute=59)
scheduler.add_job(id='3',func=sendEmail,trigger='cron', hour=14, minute=56)

scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run()