import os
import pandas as pd
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import time
from jinja2 import Template
from generar_certificado_asistencia import generar_certificado_con_qr

load_dotenv()

SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_ALIAS = os.getenv('EMAIL_SENDER')

HTML_TEMPLATE = """\
<html>
<head></head>
<body>
    <p>Hola {{nombre}},</p>
    
    <p>Gracias por inscribirte en la charla <strong>{{charla}}</strong>.</p>
    
    <p>Adjunto encontrarás tu certificado de inscripción con el código QR:</p>
    
    <p>Por favor, presenta este código QR al ingresar al evento.</p>
    
    <p>Saludos,<br>
    Equipo Organizador</p>
</body>
</html>
"""

# Configuracion de logging
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

def limpiar_nombre_charla(nombre_archivo):
    nombre = os.path.splitext(nombre_archivo)[0]
    nombre = nombre.replace('(respuestas)', '').strip()
    return nombre

def enviar_correo(destinatario, nombre, certificado_path, charla, smtp):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Confirmación de asistencia a la charla: {charla}"
        msg['From'] = EMAIL_ALIAS
        msg['To'] = destinatario
        msg['Reply-To'] = EMAIL_SENDER
        msg['X-Mailer'] = 'UTN FRLP Script'

        # Cuerpo del mensaje
        template = Template(HTML_TEMPLATE)
        html_content = template.render(nombre=nombre, charla=charla)
        msg.attach(MIMEText(html_content, 'html'))

        # Adjunta el certificado con QR
        with open(certificado_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename='certificado_inscripcion.png')
            msg.attach(img)

        smtp.send_message(msg)
        logging.info(f"Correo enviado a {destinatario}")
        return True
    except Exception as e:
        logging.error(f"Error al enviar correo a {destinatario}: {e}")
        return False

def recorrer_y_enviar():
    logging.info(f"Buscando archivos en: {BASE_DIR}")
    k = 0
    k_max = 10
    smtp = None

    for root, dirs, files in os.walk(BASE_DIR):
        logging.info(f"Revisando carpeta: {root}")
        for file in files:
            if file.endswith('.csv'):
                charla = limpiar_nombre_charla(file)
                path_csv = os.path.join(root, file)
                logging.info(f"Procesando: {path_csv} (charla: {charla})")
                
                try:
                    df = pd.read_csv(path_csv)
                    logging.info(f"{len(df)} participantes encontrados")
                    
                    for _, fila in df.iterrows():
                        email = fila.get('Mail')
                        if not email or pd.isna(email):
                            logging.warning(f"Fila sin email: {fila}")
                            continue
                            
                        nombre = fila.get('Nombre', 'participante')
                        legajo = fila.get('Legajo', '')
                        dni = fila.get('DNI', '')

                        info_qr = f"{charla};{legajo};{dni};"
                        
                        # Genera certificado con QR
                        certificado_path = generar_certificado_con_qr(info_qr)
                        
                        # Maneja conexión SMTP
                        if smtp is None:
                            logging.info("Estableciendo conexión SMTP...")
                            smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                            smtp.starttls()
                            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                        
                        # Envia correo
                        if enviar_correo(email, nombre, certificado_path, charla, smtp):
                            k += 1
                            os.remove(certificado_path)  # Limpia archivo temporal
                            
                            if k >= k_max:
                                logging.info(f"Reiniciando conexión después de {k_max} correos")
                                smtp.quit()
                                smtp = None
                                k = 0
                                time.sleep(2)
                        else:
                            if smtp:
                                try:
                                    smtp.quit()
                                except:
                                    pass
                                smtp = None
                                k = 0
                                time.sleep(5)
                
                except Exception as e:
                    logging.error(f"Error procesando {path_csv}: {e}")
                    if smtp:
                        try:
                            smtp.quit()
                        except:
                            pass
                        smtp = None
                        k = 0

    if smtp:
        logging.info("Cerrando conexión SMTP final")
        try:
            smtp.quit()
        except:
            pass

if __name__ == '__main__':
    recorrer_y_enviar()