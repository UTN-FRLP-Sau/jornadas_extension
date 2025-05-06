import os
import pandas as pd
import smtplib
import logging
import qrcode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import time

load_dotenv()

SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, 'enviar_correos.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'inscripciones')
BASE_DIR = os.path.abspath(BASE_DIR)

CUERPO = """\
Hola {nombre},

Gracias por inscribirte en la charla "{charla}".

Adjuntamos tu código QR con los detalles de tu inscripción.

Saludos,
Equipo Organizador
"""

def limpiar_nombre_charla(nombre_archivo):
    nombre = os.path.splitext(nombre_archivo)[0]
    nombre = nombre.replace('(respuestas)', '').strip()
    return nombre

def generar_qr(info):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(info)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    qr_path = 'qr_temp.png'
    img.save(qr_path)
    return qr_path

def enviar_correo(destinatario, nombre, qr_path, charla):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Confirmación de asistencia a la charla: {charla}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = destinatario
        msg['Reply-To'] = EMAIL_SENDER
        msg['X-Mailer'] = 'UTN FRLP Script'

        body = MIMEText(CUERPO.format(nombre=nombre, charla=charla), 'plain')
        msg.attach(body)

        with open(qr_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename='codigo_qr.png')
            msg.attach(img)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
            logging.info(f"Correo enviado a {destinatario}")
    except Exception as e:
        logging.error(f"Error al enviar correo a {destinatario}: {e}")

def recorrer_y_enviar():
    logging.info(f"Buscando archivos en: {BASE_DIR}")
    for root, dirs, files in os.walk(BASE_DIR):
        logging.info(f"Revisando carpeta: {root}")
        for file in files:
            logging.info(f"Encontrado archivo: {file}")
            if file.endswith('.csv'):
                charla = limpiar_nombre_charla(file)
                path_csv = os.path.join(root, file)
                logging.info(f"Leyendo archivo CSV: {path_csv} (charla: {charla})")
                try:
                    df = pd.read_csv(path_csv)
                    logging.info(f"{len(df)} filas leídas")
                    for _, fila in df.iterrows():
                        email = fila.get('Mail')
                        nombre = fila.get('Nombre', 'participante')
                        apellido = fila.get('Apellido', 'desconocido')
                        legajo = fila.get('Legajo', 'desconocido')
                        dni = fila.get('DNI', 'desconocido')
                        '''
                        Tiene que ser facil procesar en formato tabla. Te recomiendo que lo hagas en formato CSV, y que uses los siguientes nombres de columna:
                        info_qr = (
                            f"Charla: {charla}\n"
                            f"Nombre: {nombre} {apellido}\n"
                            f"Legajo: {legajo}\n"
                            f"DNI: {dni}\n"
                            f"Correo: {email}"
                        )
                        '''
                        info_qr = {charla}";"{nombre}";"{apellido}";"{legajo}";"{dni}")
                        qr_path = generar_qr(info_qr)

                        logging.info(f"Preparando correo para: {email} - {nombre}")
                        if pd.notnull(email):
                            enviar_correo(email, nombre, qr_path, charla)
                            time.sleep(1)

                        os.remove(qr_path)

                except Exception as e:
                    logging.error(f"Error al procesar {path_csv}: {e}")

if __name__ == '__main__':
    recorrer_y_enviar()
