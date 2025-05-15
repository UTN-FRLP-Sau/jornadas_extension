import os
import pandas as pd
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from jinja2 import Template
import re

load_dotenv()

REINTENTAR_TODOS = False

SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_ALIAS = os.getenv('EMAIL_SENDER')

# Template de reprogramacion
template_path = os.path.join(os.path.dirname(__file__), 'template2.html')
with open(template_path, 'r', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

# Log específico para reprogramacion
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'enviar_reprogramacion.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Ruta especifica al directorio de inscripciones de quimica
QUIMICA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'inscripciones', 'quimica'))

def obtener_emails_fallidos_desde_log(log_path):
    emails_fallidos = set()
    emails_exitosos = set()

    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='latin-1') as log_file:
            for linea in log_file:
                match_error = re.search(r'Error al enviar correo a (.+?) para la charla (\S+)', linea)
                if match_error:
                    email = match_error.group(1).strip()
                    charla = match_error.group(2).strip()
                    emails_fallidos.add((email, charla))
                    continue

                match_ok = re.search(r'Correo enviado a (.+?) para la charla: (\S+)', linea)
                if match_ok:
                    email = match_ok.group(1).strip()
                    charla = match_ok.group(2).strip()
                    emails_exitosos.add((email, charla))
    return emails_fallidos, emails_exitosos

def enviar_correo_reprogramacion(destinatario, nombre, charla, smtp):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Aviso importante - Cambios en la asignación de aulas"
        msg['From'] = EMAIL_ALIAS
        msg['To'] = destinatario
        msg['Reply-To'] = EMAIL_SENDER
        msg['X-Mailer'] = 'UTN FRLP Script'

        template = Template(HTML_TEMPLATE)
        html_content = template.render(nombre=nombre, charla=charla)
        msg.attach(MIMEText(html_content, 'html'))

        smtp.send_message(msg)
        logging.info(f"Correo enviado a {destinatario} para la charla: {charla}")
        return True
    except Exception as e:
        logging.error(f"Error al enviar correo a {destinatario} para la charla {charla}: {e}")
        return False

def recorrer_y_enviar_reprogramacion():
    smtp = None
    k = 0
    k_max = 10

    emails_fallidos, emails_exitosos = obtener_emails_fallidos_desde_log(log_file_path)
    primer_envio = not os.path.exists(log_file_path) or os.path.getsize(log_file_path) == 0

    procesadas_path = os.path.join(QUIMICA_DIR, 'procesadas')
    if not os.path.exists(procesadas_path):
        logging.warning(f"No existe la carpeta 'procesadas' en quimica: {procesadas_path}")
        return

    for charla_dir in os.listdir(procesadas_path):
        charla_path = os.path.join(procesadas_path, charla_dir)
        if not os.path.isdir(charla_path):
            continue

        charla = charla_dir
        archivo_csv = f"{charla}.csv"
        path_csv = os.path.join(charla_path, archivo_csv)

        if not os.path.exists(path_csv):
            logging.warning(f"No se encontro el archivo CSV esperado: {path_csv}")
            continue

        logging.info(f"Procesando: {path_csv} (charla: {charla})")

        try:
            df = pd.read_csv(path_csv)
            logging.info(f"{len(df)} participantes encontrados")

            for _, fila in df.iterrows():
                email = fila.get('Mail')
                if not email or pd.isna(email):
                    logging.warning(f"Fila sin email: {fila}")
                    continue

                if (REINTENTAR_TODOS or
                    primer_envio or 
                    (email, charla) in emails_fallidos or 
                    ((email, charla) not in emails_exitosos and (email, charla) not in emails_fallidos)):
                    
                    nombre = fila.get('Nombre', 'Asistente')

                    if smtp is None:
                        logging.info("Estableciendo conexion SMTP...")
                        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                        smtp.starttls()
                        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)

                    if enviar_correo_reprogramacion(email, nombre, charla, smtp):
                        k += 1
                        if k >= k_max:
                            logging.info(f"Reiniciando conexion despues de {k_max} correos")
                            smtp.quit()
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
        logging.info("Cerrando conexion SMTP final")
        try:
            smtp.quit()
        except:
            pass

if __name__ == '__main__':
    recorrer_y_enviar_reprogramacion()
