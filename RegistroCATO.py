from flask import Flask
from flask_apscheduler import APScheduler
import paramiko
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import re
import pyautogui
import pygetwindow as gw

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True

# Inicializar app flask
app = Flask(__name__)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()

def captureCmdScreenshot(local_path):

    # Encuentra la ventana del cmd por título
    cmd_window = gw.getWindowsWithTitle('cmd')[0]  # Ajusta según el título de tu ventana de cmd

    # Activar la ventana del cmd
    cmd_window.activate()

    # Maximizar la ventana del cmd
    cmd_window.maximize()

    time.sleep(2)

    # Capturar la pantalla completa
    #screenshot = pyautogui.screenshot()
   
    # Capturar la ventana activa
    screenshot = pyautogui.screenshot(region=(cmd_window.left, cmd_window.top, cmd_window.width, cmd_window.height))

    # Restaurar el tamaño original de la ventana del cmd
    cmd_window.restore()

    # Guardar la captura de pantalla
    screenshot.save(local_path)

def sendEmail():
    # Configura los detalles del correo
    remitente = "raziel203619@gmail.com"  # Cambia por tu correo de dominio propio
    password = "omxr msoe idwe ccvo"  # Cambia por tu contraseña
    destinatarios = ['carl.acevedoa@duocuc.cl']
    asunto = 'Captura de Pantalla estado CATO'
    cuerpo = 'Se adjunta captura de pantalla estado CATO.'

    # Configura el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Configura el servidor SMTP de Gmail
    servidor_smtp = "smtp.gmail.com"
    #smtp-mail.outlook.com

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

def validateTunnelStatus(output, local_path):
    # Convierte el log en un string
    log = str(output)

    # busca las palabras UP o DOWN en la palabra Status.
    status_matches = re.findall(r'Status: (UP|DOWN)', log)

    print(r'Status Actual: ',status_matches)

    tunel1 = status_matches[0]
    tunel2 = status_matches[1]
    tunel3 = status_matches[2]

    print(r'Status tunel 1: ', tunel1)
    print(r'Status tunel 2: ', tunel2)
    print(r'Status tunel 3: ', tunel3)

    if tunel1 == 'UP' and tunel2 == 'UP' and tunel3 == 'UP':
        # Captura la ventana del cmd y guarda la imagen
        time.sleep(2)
        captureCmdScreenshot(local_path)
        # Envía el correo electrónico con la captura de pantalla adjunta
        correo_enviado = sendEmail("cacevedo@acdata.cl", local_path)
        if correo_enviado:
            print("Correo enviado exitosamente.")
        else:
            print("Error al enviar el correo.")
    else:
        # Captura la ventana del cmd y guarda la imagen
        time.sleep(2)
        captureCmdScreenshot(local_path)
        # Envía el correo electrónico con la captura de pantalla adjunta
        correo_enviado = sendEmail("cacevedo@acdata.cl", local_path)
        if correo_enviado:
            print("Correo enviado exitosamente.")
        else:
            print("Error al enviar el correo.")

def main():
    # Configuración de la conexión SSH
    hostname = '192.168.31.1'
    port = 22
    username = 'admin'
    password = 'Fynsa_Edge2021@'

    # Crear una instancia de la clase SSHClient
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conectar al servidor
        ssh.connect(hostname, port, username, password)

        # Ejecutar comandos SSH de manera interactiva
        channel = ssh.invoke_shell()

        comandos = [
            'show service ipsec',
            # Agrega más comandos según tus necesidades
        ]

        for comando in comandos:
            print(f"Ejecutando comando: {comando}")
           
            # Ejecuta el comando
            channel.send(comando + '\n')

            # Espera un tiempo para que el comando se ejecute
            time.sleep(3)

            # Lee la salida
            output = channel.recv(4096).decode()

            # Imprime la salida
            print(f"Resultado de '{comando}':")
            print(output)

        # Encuentra la ventana del cmd
       
        # Definir la ruta local para guardar la captura de pantalla
        local_path = f"screenshots/local_screenshot_{time.time()}.png"

        # Valida el estado del túnel y envía el correo
        validateTunnelStatus(output, local_path)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cerrar la conexión SSH
        ssh.close()

scheduler.add_job(id='1',func=main,trigger='cron', hour=3, minute=51)
scheduler.add_job(id='2',func=main,trigger='cron', hour=3, minute=52)
scheduler.add_job(id='3',func=main,trigger='cron', hour=3, minute=53)

scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run()