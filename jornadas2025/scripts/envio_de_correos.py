import os
import pandas as pd
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from jinja2 import Template
from generar_certificado_asistencia import generar_certificado_con_qr

load_dotenv()

SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_ALIAS = os.getenv('EMAIL_SENDER')

# Ruta al template
template_path = os.path.join(os.path.dirname(__file__), 'template.html')

# Leer el contenido del archivo HTML una sola vez
with open(template_path, 'r', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

# Configuración de logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, 'enviar_correos.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Directorio base donde están los departamentos
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'inscripciones')
BASE_DIR = os.path.abspath(BASE_DIR)

def limpiar_nombre_charla(nombre_archivo):
    """
    Extrae el nombre legible de la charla a partir del archivo 'limpio_xxx.csv'
    """
    nombre = os.path.splitext(nombre_archivo)[0]  # sin extensión
    if nombre.startswith("limpio_"):
        nombre = nombre[len("limpio_"):]  # quitar prefijo
    nombre = nombre.replace('_', ' ').strip().title()
    return nombre

def enviar_correo(destinatario, nombre, certificado_path, charla, smtp):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"QR de asistencia para la charla: {charla} - Jornadas de Formación Profesional 2025"
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
            img.add_header('Content-ID', '<certificado>')
            img.add_header('Content-Disposition', 'inline', filename='certificado_inscripcion.png')
            msg.attach(img)

        smtp.send_message(msg)
        logging.info(f"Correo enviado a {destinatario} para la charla: {charla}")
        return True
    except Exception as e:
        logging.error(f"Error al enviar correo a {destinatario} para la charla {charla}: {e}")
        return False

def recorrer_y_enviar():
    logging.info(f"Buscando archivos en: {BASE_DIR}")
    k = 0
    k_max = 10
    smtp = None

    for departamento in os.listdir(BASE_DIR):
        depto_path = os.path.join(BASE_DIR, departamento)
        if not os.path.isdir(depto_path):
            continue

        limpias_path = os.path.join(depto_path, 'inscripciones-limpias')
        if not os.path.exists(limpias_path):
            continue

        for file in os.listdir(limpias_path):
            if not file.startswith('limpio_') or not file.endswith('.csv'):
                continue

            charla = limpiar_nombre_charla(file)
            path_csv = os.path.join(limpias_path, file)
            logging.info(f"Procesando: {path_csv} (charla: {charla})")

            try:
                df = pd.read_csv(path_csv)
                logging.info(f"{len(df)} participantes encontrados")

                for _, fila in df.iterrows():
                    email = fila.get('Mail')
                    if not email or pd.isna(email):
                        logging.warning(f"Fila sin email: {fila}")
                        continue

                    nombre = fila.get('Nombre', 'Participante')
                    legajo = fila.get('Legajo', '')
                    dni = fila.get('DNI', '')

                    info_qr = f"{charla};{legajo};{dni};"

                    # Genera certificado con QR
                    certificado_path = generar_certificado_con_qr(info_qr, charla)

                    # Maneja conexión SMTP
                    if smtp is None:
                        logging.info("Estableciendo conexión SMTP...")
                        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                        smtp.starttls()
                        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)

                    # Envia correo
                    if enviar_correo(email, nombre, certificado_path, charla, smtp):
                        k += 1
                        os.remove(certificado_path)

                        if k >= k_max:
                            logging.info(f"Reiniciando conexión después de {k_max} correos")
                            smtp.quit()
                            smtp = None
                            k = 0
                    else:
                        if smtp:
                            try:
                                smtp.quit()
                            except:
                                pass
                            smtp = None
                            k = 0

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
