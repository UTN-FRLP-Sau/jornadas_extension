import os
import pandas as pd
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from jinja2 import Template
from generar_qr_asistencia import generar_qr_asistencia
import csv
from email.mime.base import MIMEBase
from email import encoders
import re

load_dotenv()

REINTENTAR_TODOS = False  # Cambiar a True para reenviar a todos, incluso a los exitosos // util para reenvio sin sin tener que eliminar el logs


SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_ALIAS = os.getenv('EMAIL_SENDER')

# Ruta al template
template_path = os.path.join(os.path.dirname(__file__), 'template.html')

# Lee el contenido del archivo HTML una sola vez
with open(template_path, 'r', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

# Configuración de logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file_path = os.path.join(log_dir, 'enviar_correos.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Directorio base donde están los departamentos
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'inscripciones')
BASE_DIR = os.path.abspath(BASE_DIR)

def transformar_codigo_charla_a_nombre_charla(codigo_charla):
    """
    Transforma un código de charla en el nombre legible de la charla, 
    buscando en el archivo CSV de referencias.
    """
    ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'inscripciones', 'tabla-de-referencias.csv')
    try:
        with open(ruta_csv, encoding='utf-8') as archivo:
            lector = csv.reader(archivo, delimiter=';')
            for fila in lector:
                if len(fila) < 3:
                    continue
                codigo, nombre_charla, _ = fila
                if codigo.strip() == codigo_charla:
                    return nombre_charla.strip()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_csv}")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
    return codigo_charla


def obtener_aula_por_codigo_charla(codigo_charla):
    """
    Dado un código de charla, retorna el aula correspondiente
    según el archivo 'tabla-de-referencias.csv'.

    Returns:
        str: Aula de la charla, o el código si no se encuentra.
    """
    ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'inscripciones', 'tabla-de-referencias.csv')
    try:
        with open(ruta_csv, encoding='utf-8') as archivo:
            lector = csv.reader(archivo, delimiter=';')
            for fila in lector:
                if len(fila) < 3:
                    continue
                codigo, _, aula = fila
                if codigo.strip() == codigo_charla:
                    return aula.strip()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_csv}")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
    return codigo_charla


def obtener_emails_fallidos_desde_log(log_path):
    """
    Obtiene la lista de (email, charla) exitosos y fallidos del log.
    """
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


def enviar_correo(destinatario, nombre, qr_path, charla, smtp):
    """
    Envía un correo electrónico con el qr de asistencia.

    Args:
        destinatario (str): Dirección de correo electrónico del destinatario.
        nombre (str): Nombre del participante.
        qr_path (str): Ruta al archivo del qr.
        charla (str): Nombre de la charla.
        smtp (smtplib.SMTP): Conexión SMTP.

    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario.
    """
    try:
        # Transformo el código de charla a nombre legible
        charla_nombre = transformar_codigo_charla_a_nombre_charla(charla)

        msg = MIMEMultipart()
        msg['Subject'] = f"QR de asistencia: {charla_nombre}"
        msg['From'] = EMAIL_ALIAS
        msg['To'] = destinatario
        msg['Reply-To'] = EMAIL_SENDER
        msg['X-Mailer'] = 'UTN FRLP Script'

        # Cuerpo del mensaje
        template = Template(HTML_TEMPLATE)

        aula = obtener_aula_por_codigo_charla(charla)

        html_content = template.render(nombre=nombre, charla=charla_nombre, aula=aula)
        msg.attach(MIMEText(html_content, 'html'))

        # Adjunta el QR
        with open(qr_path, 'rb') as f:
            adjunto = MIMEBase('application', 'octet-stream')
            adjunto.set_payload(f.read())
            encoders.encode_base64(adjunto)
            adjunto.add_header(
                'Content-Disposition',
                f'attachment; filename="qr_asistencia_{nombre}.png"'
            )
            msg.attach(adjunto)

        smtp.send_message(msg)
        logging.info(f"Correo enviado a {destinatario} para la charla: {charla}")
        return True
    except Exception as e:
        logging.error(f"Error al enviar correo a {destinatario} para la charla {charla}: {e}")
        return False

def recorrer_y_enviar():
    k = 0
    k_max = 10
    smtp = None

    # Obtiene emails fallidos y exitosos del log
    emails_fallidos, emails_exitosos = obtener_emails_fallidos_desde_log(log_file_path)
    
    # Determina si es el primer envio (cuando no hay logs o esta vacio)
    primer_envio = not os.path.exists(log_file_path) or os.path.getsize(log_file_path) == 0
        
    for departamento in os.listdir(BASE_DIR):
        depto_path = os.path.join(BASE_DIR, departamento)
        if not os.path.isdir(depto_path):
            continue

        procesadas_path = os.path.join(depto_path, 'procesadas')
        if not os.path.exists(procesadas_path):
            continue

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

                    # verifica: si es el primer envio, si la combinación email+charla está en fallidos, si es un nuevo mail, o si reintentar todos es true
                    if (REINTENTAR_TODOS or
                        primer_envio or 
                        (email, charla) in emails_fallidos or 
                        ((email, charla) not in emails_exitosos and (email, charla) not in emails_fallidos)):
                        
                        nombre = fila.get('Nombre', 'Asistente')
                        legajo = fila.get('Legajo', '')
                        dni = fila.get('DNI', '')

                        info_qr = f"{charla};{legajo};{dni};"

                        # Genera QR
                        qr_path = generar_qr_asistencia(info_qr, charla)
                        
                        # Maneja conexión SMTP
                        if smtp is None:
                            logging.info("Estableciendo conexion SMTP...")
                            smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                            smtp.starttls()
                            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                        
                        # Envia correo
                        if enviar_correo(email, nombre, qr_path, charla, smtp):
                            k += 1
                            os.remove(qr_path)

                            if k >= k_max:
                                logging.info(f"Reiniciando conexion después de {k_max} correos")
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
    recorrer_y_enviar()