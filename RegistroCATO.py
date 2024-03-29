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

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True

# Inicializar app flask
app = Flask(__name__)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()

# Configuración de la conexión SSH
hostname = '192.168.31.1'
port = 22
username = 'admin'
password = 'Fynsa_Edge2021@'

# Definir la ruta local para guardar la captura de pantalla
local_path = f"screenshots/local_screenshot_{time.time()}.png"

def createImageFromLog(log):
    # Configura el tamaño y el formato de la imagen
    image_width = 800
    image_height = 600
    background_color = (0, 0, 0)  # Fondo negro
    text_color = (255, 255, 255)  # Texto blanco

    # Crea una imagen en blanco con fondo negro
    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    # Carga una fuente monoespaciada que asemeje el estilo de consola
    font_path = "consola.ttf"  # Descarga una fuente de consola monoespaciada

    try:
        font = ImageFont.truetype(font_path, 14)
    except IOError:
        # Si la fuente no está disponible, utiliza la fuente por defecto
        font = ImageFont.load_default()

    # Divide el log en líneas
    lines = log.split('\n')

    # Escribe cada línea en la imagen con el estilo de consola
    y_position = 10
    for line in lines:
        draw.text((10, y_position), line, font=font, fill=text_color)
        y_position += 18  # Ajusta el espacio entre líneas según sea necesario

    # Guarda la imagen
    image.save(local_path)

def sendEmail(destinatario, asunto, body):

    # Configura los detalles del correo
    remitente = "cacevedo@acdata.cl"  # Cambia por tu correo de dominio propio
    password = "ljfmfgmdxfcqngqk"  # Cambia por tu contraseña  zghpsnvpplzkjhjj BotReporteCATO

    destinatarios = [destinatario]
    subject = asunto
    cuerpo = body
    ruta_adjunto = local_path

    # Configura el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = subject
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    if(ruta_adjunto):

        # Adjunta la imagen al mensaje
        with open(ruta_adjunto, 'rb') as adjunto:
            imagen_adjunta = MIMEImage(adjunto.read(), name=f'captura_{time.time()}.png')
        mensaje.attach(imagen_adjunta)

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
    mail.login(email_user, email_password)
    mail.select("inbox")

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
    print("Esperando correos pendientes ...")
    receiveEmail(["Reiniciar tuneles", "Actualizar estado", "Consulta estado"])  # Puedes añadir más instrucciones según sea necesario

def validateTunnelStatus(output):
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
       
        time.sleep(1)
        # Crea una imagen y copia el status del tunnel
        createImageFromLog(log)

        # Obtener la fecha y hora actual
        fecha_hora_actual = datetime.now()
        # Formatear la fecha y hora en el formato deseado
        formato_deseado = "%d-%m-%Y %H:%M"
        fecha_hora_formateada = fecha_hora_actual.strftime(formato_deseado)
        status_tunnel = f'Estimados:\n\n Adjuntamos estado cato del dia de hoy. \n\n{log}'

        asunto = f'ESTADO CATO {fecha_hora_formateada}'

        correo_enviado = sendEmail('fynsabottest@gmail.com', asunto, status_tunnel)

        if correo_enviado:
            print("Correo enviado exitosamente.")
        else:
            print("Error al enviar el correo.")
    else:
        
        time.sleep(2)

        #captureCmdScreenshot(local_path)
        createImageFromLog(log)

        # Obtener la fecha y hora actual
        fecha_hora_actual = datetime.now()
        # Formatear la fecha y hora en el formato deseado
        formato_deseado = "%d-%m-%Y %H:%M"
        fecha_hora_formateada = fecha_hora_actual.strftime(formato_deseado)

        asunto = f'ESTADO CATO {fecha_hora_formateada}'

        status_tunnel = f'Estimados:\n\n Se indica registro de error en cato: \n\n{log}'
        
        # Envía el correo electrónico con la captura de pantalla adjunta
        correo_enviado = sendEmail('fynsabottest@gmail.com', asunto, status_tunnel)

        if correo_enviado:
            print("Correo enviado exitosamente.")
        else:
            print("Error al enviar el correo.")

def main():

    # Realiza la conexion SSH al servidor y obtiene el registro del comando indicado.
    output = connectSSH('show service ipsec')

    # Se valida el registro del comando y se envia a traves de correo electronico
    validateTunnelStatus(output)


def connectSSH(comand):
    # Crear una instancia de la clase SSHClient
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conectar al servidor
        ssh.connect(hostname, port, username, password)

        # Ejecutar comandos SSH de manera interactiva
        channel = ssh.invoke_shell()

        print(f"Ejecutando comando: {comand}")
                        
        # Ejecuta el comando
        channel.send(comand + '\n')

        # Espera un tiempo para que el comando se ejecute
        time.sleep(3)

        # Lee la salida
        output = channel.recv(4096).decode()

        # Imprime la salida
        print(f"Resultado de '{comand}':")
        print(output)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cerrar la conexión SSH
        ssh.close()

    return output

scheduler.add_job(id='1',func=main,trigger='cron', hour=16, minute=0)
scheduler.add_job(id='2',func=main,trigger='cron', hour=16, minute=1)
scheduler.add_job(id='3',func=main,trigger='cron', hour=16, minute=2)

scheduler.add_job(id='4',func=receiveEmailWrapper,trigger='interval', minutes=0.1)

scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run()