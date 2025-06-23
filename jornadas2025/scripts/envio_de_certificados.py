import os
import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from dotenv import load_dotenv
import re
from email.header import Header
from email.utils import formataddr

# --- Configuración inicial ---
load_dotenv()

REINTENTAR_TODOS = False  # Cambiar a True para reenviar a todos, incluso a los exitosos

SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_ALIAS = os.getenv('EMAIL_ALIAS')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CERTIFICADOS_DIR = os.path.join(BASE_DIR, 'certificados')
MAP_FILE = os.path.join(CERTIFICADOS_DIR, 'certificados_a_enviar.json')

# --- Template HTML ---
template_path = os.path.join(os.path.dirname(__file__), 'template-certificados.html')
with open(template_path, encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

# --- Logging ---
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(logs_dir, exist_ok=True)
log_path = os.path.join(logs_dir, 'enviar-certificados.log')

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Funciones ---

def obtener_registros_log():
    exitosos = set()
    fallidos = set()
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='latin-1') as f:
                for linea in f:
                    # Captura destinatario, nombre y subcarpeta en el log
                    match_ok = re.search(r'Correo enviado a (.+?) \((.+?)\) \[subcarpeta: (.+?)\]', linea)
                    match_error = re.search(r'Error al enviar correo a (.+?) \((.+?)\) \[subcarpeta: (.+?)\]', linea)
                    if match_ok:
                        clave = (match_ok.group(1), match_ok.group(2), match_ok.group(3))
                        fallidos.discard(clave)
                        exitosos.add(clave)
                    elif match_error:
                        clave = (match_error.group(1), match_error.group(2), match_error.group(3))
                        fallidos.add(clave)
        except Exception as e:
            # Captura si hay un problema al abrir o leer el log por alguna otra razón
            logging.error(f"Error al leer el archivo de log '{log_path}': {e}")
    return exitosos, fallidos

def enviar_certificado(destinatario, nombre, subcarpeta, pdf_path, smtp):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Certificado de asistencia y encuesta - Jornadas de Formación Profesional"
        msg['From'] = formataddr((str(Header(EMAIL_ALIAS, 'utf-8')), EMAIL_SENDER))
        msg['To'] = destinatario
        msg['Reply-To'] = EMAIL_SENDER

        # Cuerpo HTML
        template = Template(HTML_TEMPLATE)
        html_content = template.render(nombre=nombre)
        msg.attach(MIMEText(html_content, 'html'))

        # Adjuntar PDF
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'pdf')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(pdf_path)}"'
            )
            msg.attach(part)

        smtp.send_message(msg)
        logging.info(f"Correo enviado a {destinatario} ({nombre}) [subcarpeta: {subcarpeta}]")
        return True
    except Exception as e:
        logging.error(f"Error al enviar correo a {destinatario} ({nombre}) [subcarpeta: {subcarpeta}]: {e}")
        return False

def recorrer_y_enviar():
    if not os.path.exists(MAP_FILE):
        logging.error(f"No se encontro el archivo de mapeo: {MAP_FILE}")
        return

    with open(MAP_FILE, encoding='utf-8') as f: 
        certificados = json.load(f)

    envios_ok, envios_fallidos = obtener_registros_log()

    smtp = None
    intentos = 0
    max_por_conexion = 10

    for entry in certificados:
        email = entry['correo_destinatario']
        nombre = entry['nombre_completo']
        subcarpeta = entry['subcarpeta_dia']
        pdf_name = entry['nombre_pdf_generado']
        pdf_path = os.path.join(CERTIFICADOS_DIR, subcarpeta, pdf_name)

        if not os.path.exists(pdf_path):
            logging.error(f"Certificado no encontrado para {nombre}: {pdf_path}")
            continue

        clave = (email, nombre, subcarpeta)

        if not REINTENTAR_TODOS:
            if clave in envios_ok:
                continue
            # No se saltea si está en fallidos o no está en ninguno (para intentar enviar)
        
        if smtp is None:
            try:
                smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                smtp.starttls()
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                logging.info("Conexion SMTP establecida.")
            except Exception as e:
                logging.error(f"Fallo al conectar al servidor SMTP: {e}")
                return

        if enviar_certificado(email, nombre, subcarpeta, pdf_path, smtp):
            intentos += 1

        if intentos >= max_por_conexion:
            smtp.quit()
            smtp = None
            intentos = 0

    if smtp:
        smtp.quit()

# --- Main ---
if __name__ == '__main__':
    recorrer_y_enviar()
