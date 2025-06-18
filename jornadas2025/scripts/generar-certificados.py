import pandas as pd
from fpdf import FPDF
import pikepdf
import os
from datetime import date
import unicodedata
import json
from pypdf import PdfReader
import argparse

# --- Configuración de Rutas y Fuentes ---

# directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# directorio del proyecto
PROYECTO_DIR = os.path.dirname(BASE_DIR)

# directorio de la fuente
FONT_PATH = os.path.join(PROYECTO_DIR, 'fonts', 'Planc-wfx', 'Planc-Bold.otf')

# Nombre de la fuente
CUSTOM_FONT_NAME = 'Planc-Bold'

# Ruta al PDF base
TEMPLATE_PDF_PATH = os.path.join(BASE_DIR, 'certificado-jfp-2025.pdf')


'''
ruta_plantilla = TEMPLATE_PDF_PATH

# Abrir PDF
reader = PdfReader(ruta_plantilla)
pagina = reader.pages[0]

# Obtener tamaño en puntos (pt)
media_box = pagina.mediabox
ancho_pts = float(media_box.width)
alto_pts = float(media_box.height)

# Convertir puntos a milímetros (1 punto = 0.3527777778 mm)
ancho_mm = ancho_pts * 0.3527777778
alto_mm = alto_pts * 0.3527777778

print(f"Ancho plantilla: {ancho_mm:.2f} mm")
print(f"Alto plantilla: {alto_mm:.2f} mm")'''

# Ruta para el archivo de mapeo de correos
# Este archivo guardará el nombre del PDF, la subcarpeta y el correo.
EMAIL_MAP_FILE = os.path.join(PROYECTO_DIR, 'certificados' ,'certificados_a_enviar.json')

def generar_contenido_certificado_overlay(nombre_completo, documento, temp_output_pdf):
    """
    Genera el contenido dinámico del certificado (nombre y DNI) en un PDF temporal
    usando FPDF2. Este PDF temporal luego se superpondrá a la plantilla base.
    """
    pdf = FPDF(unit='mm', format=(297, 210))
    pdf.add_page()

    # Registro la fuente personalizada
    global CUSTOM_FONT_NAME

    try:
        pdf.add_font(CUSTOM_FONT_NAME, '', FONT_PATH)
    except Exception as e:
        print(f"Error al registrar la fuente '{CUSTOM_FONT_NAME}' con FPDF2: {e}")
        CUSTOM_FONT_NAME = "Helvetica"
        print(f"Usando 'Helvetica' como fuente de respaldo para FPDF2.")

    # --- Contenido Dinámico ---

    font_size_nombre = 31
    font_size_dni = 31
    y_nombre_mm = 93
    y_dni_mm = y_nombre_mm + 15

    # Preparación del texto
    nombre_completo = nombre_completo.upper()

    # Quitar márgenes
    pdf.set_left_margin(0)
    pdf.set_right_margin(0)

    # Setear color
    pdf.set_text_color(43, 79, 254)

    # Dimensiones de la caja fija
    fixed_width = 270
    fixed_height = 20
    x_fixed = (pdf.w - fixed_width) / 2

    # --- CENTRADO DE NOMBRE (en caja fija y sin cortes) ---
    pdf.set_font(CUSTOM_FONT_NAME, '', font_size_nombre)
    text_width = pdf.get_string_width(nombre_completo)

    # Si no entra, escala fuente
    if text_width > fixed_width:
        scale = fixed_width / text_width
        adjusted_font_size = font_size_nombre * scale
        pdf.set_font(CUSTOM_FONT_NAME, '', adjusted_font_size)

    # Dibuja cell con el nombre centrado en caja
    pdf.set_xy(x_fixed, y_nombre_mm)
    pdf.cell(w=fixed_width, h=fixed_height, text=nombre_completo, align='C', border=0)

    # --- CENTRADO DEL DNI ---
    pdf.set_font(CUSTOM_FONT_NAME, '', font_size_dni)
    text_dni = f"DNI: {documento}"
    text_dni_width = pdf.get_string_width(text_dni)

    # Escala fuente si no entra
    if text_dni_width > fixed_width:
        scale_dni = fixed_width / text_dni_width
        adjusted_font_size_dni = font_size_dni * scale_dni
        pdf.set_font(CUSTOM_FONT_NAME, '', adjusted_font_size_dni)

    pdf.set_xy(x_fixed, y_dni_mm)
    pdf.cell(w=fixed_width, h=fixed_height, text=text_dni, align='C', border=0)

    
    # Fecha de Emisión
    '''
    meses_espanol = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    fecha_actual = date.today()
    
    # Coordenadas para la fecha
    # x_fecha_mm: 25.4 mm es 1 pulgada desde el borde izquierdo.
    # y_fecha_mm: pdf.h - 38.1 es 1.5 pulgadas desde el borde inferior (pdf.h es la altura total de la página).
    x_fecha_mm = 25.4 
    y_fecha_mm = pdf.h - 38.1 
    
    pdf.set_font("Helvetica", '', 10) 
    pdf.set_xy(x_fecha_mm, y_fecha_mm)
    pdf.write(5, f"Fecha de Emisión: {fecha_actual.day} de {meses_espanol[fecha_actual.month - 1]} de {fecha_actual.year}")
    pdf.set_xy(x_fecha_mm, y_fecha_mm + 5) # 5 mm hacia abajo para la siguiente línea
    pdf.write(5, "Berisso, Buenos Aires, Argentina")
    '''

    pdf.output(temp_output_pdf) # Guarda el PDF temporal con el contenido dinámico


def generar_certificado_final(nombre_completo, documento, ruta_salida_pdf):
    """
    Combina el contenido dinámico generado en un PDF temporal con la plantilla base
    usando pikepdf para una fusión robusta.
    """
    # 1. Generar el contenido dinámico en un PDF temporal
    temp_overlay_pdf = os.path.join(BASE_DIR, "temp_overlay.pdf")
    generar_contenido_certificado_overlay(nombre_completo, documento, temp_overlay_pdf)

    # # --- DEPURACIÓN: ABRIR temp_overlay_pdf para verificar ---
    # print(f"DEBUG: Verifica el archivo temporal: {temp_overlay_pdf}")
    # input("Pulsa Enter después de verificar temp_overlay.pdf...") # Pausa el script

    # --- Fusión de PDFs usando pikepdf ---
    try:
        # Abre el PDF base (plantilla)
        with pikepdf.open(TEMPLATE_PDF_PATH) as pdf_base:
            # Abre el PDF con el contenido dinámico (overlay)
            with pikepdf.open(temp_overlay_pdf) as pdf_overlay:
                # Superpone la primera página del overlay sobre la primera página de la base
                pdf_base.pages[0].add_overlay(pdf_overlay.pages[0])
            
            # Guarda el PDF resultante
            pdf_base.save(ruta_salida_pdf)
        
        # Eliminar el archivo temporal
        os.remove(temp_overlay_pdf)

    except Exception as e:
        print(f"Error al fusionar PDFs con pikepdf para '{nombre_completo}': {e}")
        if os.path.exists(temp_overlay_pdf):
            os.remove(temp_overlay_pdf)


def procesar_csvs_y_generar_certificados(carpeta_csvs='asistencias', subcarpeta_origen='procesadas', carpeta_certificados='certificados', max_registros_test=2):
    """
    Procesa los primeros 'max_registros_test' de cada archivo CSV de la subcarpeta 'procesadas',
    genera certificados y los guarda en la estructura de carpetas deseada.
    Establece max_registros_test=None para procesar todos los registros.
    """
    ruta_origen_csvs = os.path.join(PROYECTO_DIR, carpeta_csvs, subcarpeta_origen)
    ruta_certificados = os.path.join(PROYECTO_DIR, carpeta_certificados)

    # Crea la carpeta principal de certificados si no existe
    if not os.path.exists(ruta_certificados):
        os.makedirs(ruta_certificados)
        print(f"Creada carpeta principal para certificados: '{ruta_certificados}'")

    # Verifica si la carpeta de CSVs de origen existe
    if not os.path.exists(ruta_origen_csvs):
        print(f"Error: La carpeta '{ruta_origen_csvs}' no existe. Asegúrate de tener los CSVs en la ubicación correcta.")
        return
    
    # Verifica si la plantilla PDF existe
    if not os.path.exists(TEMPLATE_PDF_PATH):
        print(f"Error: La plantilla PDF '{TEMPLATE_PDF_PATH}' no se encontró en la carpeta del script. Asegúrate de que esté allí.")
        return

    # Lista todos los archivos CSV en la carpeta de origen
    csv_files = [f for f in os.listdir(ruta_origen_csvs) if f.endswith('.csv')]

    if not csv_files:
        print(f"No se encontraron archivos CSV en la carpeta '{ruta_origen_csvs}'.")
        return

    print(f"Iniciando generación de certificados desde los archivos CSV en '{ruta_origen_csvs}'...")
    if max_registros_test is not None:
        print(f"  (Modo de testeo: procesando solo los primeros {max_registros_test} registros por archivo)")

    # --- Lista para almacenar los datos de envío ---
    # Usamos una lista de diccionarios que luego convertiremos a DataFrame y guardaremos como JSON.
    datos_envio_list = []

    for csv_file in csv_files:
        csv_path = os.path.join(ruta_origen_csvs, csv_file)
        
        # Crea una subcarpeta dentro de 'certificados' para cada archivo CSV
        nombre_subcarpeta = os.path.splitext(csv_file)[0] # Nombre del CSV sin extensión
        ruta_subcarpeta_certificados = os.path.join(ruta_certificados, nombre_subcarpeta)

        if not os.path.exists(ruta_subcarpeta_certificados):
            os.makedirs(ruta_subcarpeta_certificados)
            print(f"Creada subcarpeta para certificados: '{ruta_subcarpeta_certificados}'")

        try:
            # Leo el archivo CSV con delimitador de punto y coma
            df = pd.read_csv(csv_path, sep=';')

            # Defino los nombres de columnas esperados
            COL_APELLIDO_NOMBRES = 'Apellido y Nombres'
            COL_DOCUMENTO = 'Documento'
            COL_MAIL = 'Mail'
            COL_MAIL_UTN = 'Mail UTN'
            
            # Verifico si las columnas esenciales existen en el DataFrame
            if not all(col in df.columns for col in [COL_APELLIDO_NOMBRES, COL_DOCUMENTO, COL_MAIL]):
                print(f"Error: Una o más columnas esenciales ('{COL_APELLIDO_NOMBRES}', '{COL_DOCUMENTO}', '{COL_MAIL}') no se encontraron en '{csv_file}'. Saltando este archivo.")
                continue

            # Verifico si al menos una de las columnas de correo existe
            if not (COL_MAIL in df.columns or COL_MAIL_UTN in df.columns):
                print(f"Error: Ninguna columna de correo ('{COL_MAIL}' o '{COL_MAIL_UTN}') encontrada en '{csv_file}'. Saltando este archivo.")
                continue

            # Determino cuántos registros procesar (todos o solo los de test)
            if max_registros_test is not None:
                df_procesar = df.head(max_registros_test)
                print(f"  Procesando los primeros {len(df_procesar)} de {len(df)} registros en '{csv_file}'.")
            else:
                df_procesar = df
                print(f"\nProcesando archivo: '{csv_file}' con {len(df_procesar)} registros.")

            # Itera sobre cada fila del DataFrame para generar certificados
            for index, row in df_procesar.iterrows():
                apellido_nombre = row[COL_APELLIDO_NOMBRES]
                documento = str(row[COL_DOCUMENTO])
                correo_electronico = None

                # Usa el campo 'Mail'
                if COL_MAIL in row and pd.notna(row[COL_MAIL]) and str(row[COL_MAIL]).strip() != '':
                    correo_electronico = str(row[COL_MAIL]).strip()
                # Si 'Mail' está vacío, no existe o es NaN, intenta usar 'Mail UTN'
                elif COL_MAIL_UTN in row and pd.notna(row[COL_MAIL_UTN]) and str(row[COL_MAIL_UTN]).strip() != '':
                    correo_electronico = str(row[COL_MAIL_UTN]).strip()

                # Si después de ambas verificaciones el correo sigue siendo nulo, se salta el registro
                if not correo_electronico:
                    print(f"Advertencia: No se encontró un correo electrónico válido para '{apellido_nombre}' (DNI: {documento}). Saltando generación de certificado.")
                    continue # Continúa con la siguiente fila en el CSV

                # Normaliza el nombre para usarlo en el nombre del archivo PDF
                nombre_limpio = unicodedata.normalize('NFKD', apellido_nombre).encode('ascii', 'ignore').decode('utf-8')
                nombre_limpio = nombre_limpio.replace(" ", "-").replace(",", "").replace(".", "").replace("'", "").lower()
                
                # Normaliza el DNI para usarlo en el nombre del archivo PDF y asegurar unicidad
                documento_limpio = str(documento).strip().replace(".", "").replace("-", "")

                # Nombre del archivo PDF final, incluyendo el DNI para unicidad
                nombre_pdf = f"{nombre_limpio}-{documento_limpio}-certificado.pdf" 
                ruta_salida_pdf = os.path.join(ruta_subcarpeta_certificados, nombre_pdf)

                # Genera el certificado final
                generar_certificado_final(apellido_nombre, documento, ruta_salida_pdf)
                print(f"  Generado certificado para '{apellido_nombre}' (DNI {documento_limpio}) en '{ruta_salida_pdf}'")

                # Agrega los datos al listado para el mapeo de correos
                datos_envio_list.append({
                    'nombre_completo': apellido_nombre,
                    'documento': documento,
                    'correo_destinatario': correo_electronico,
                    'nombre_pdf_generado': nombre_pdf,
                    'subcarpeta_dia': nombre_subcarpeta
                })

        except FileNotFoundError:
            print(f"Error: El archivo '{csv_path}' no fue encontrado.")
        except KeyError as e:
            print(f"Error: Columna esperada no encontrada en '{csv_file}'. Detalle: {e}. Asegúrate de que los encabezados estén correctos y sin espacios extra.")
        except Exception as e:
            print(f"Ocurrió un error inesperado al procesar '{csv_file}': {e}")
    
    # Guarda el Dataframe como JSON
    if datos_envio_list:
        df_envio = pd.DataFrame(datos_envio_list)
        try:
            df_envio.to_json(EMAIL_MAP_FILE, orient='records', indent=4, force_ascii=False)
            print(f"\nMapeo de certificados a correos guardado en: {EMAIL_MAP_FILE}")


        except Exception as e:
            print(f"Error al guardar el mapeo de correos en '{EMAIL_MAP_FILE}': {e}")
    else:
        print("\nNo se generaron certificados para enviar, no se creó el archivo de mapeo.")



def generar_certificado_prueba():
    """
    Genera un certificado de prueba con datos hardcodeados
    y lo guarda en certificados/prueba/.
    También actualiza el archivo certificados_a_enviar.json con esta entrada.
    """
    nombre_completo = "nombre apellido"
    documento = "123456"
    correo_destinatario = "correo@gmail.com"

    nombre_pdf_generado = "nombre-apellido-123456-certificado.pdf"
    subcarpeta_dia = "prueba"

    carpeta_destino = os.path.join(PROYECTO_DIR, "certificados", subcarpeta_dia)
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    ruta_pdf = os.path.join(carpeta_destino, nombre_pdf_generado)
    generar_certificado_final(nombre_completo, documento, ruta_pdf)
    print(f"Certificado de prueba generado: {ruta_pdf}")

    # Actualiza el JSON con el nuevo certificado
    entrada = {
        "nombre_completo": nombre_completo,
        "documento": documento,
        "correo_destinatario": correo_destinatario,
        "nombre_pdf_generado": nombre_pdf_generado,
        "subcarpeta_dia": subcarpeta_dia
    }

    try:
        if os.path.exists(EMAIL_MAP_FILE):
            with open(EMAIL_MAP_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
        else:
            datos = []

        datos.append(entrada)

        with open(EMAIL_MAP_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

        print(f"Entrada agregada a {EMAIL_MAP_FILE}")
    except Exception as e:
        print(f"Error al actualizar {EMAIL_MAP_FILE}: {e}")


# --- Ejecución del script ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de certificados UTN FRLP")
    parser.add_argument('--test', action='store_true', help="Generar certificado de prueba manual")
    parser.add_argument('--todos', action='store_true', help="Procesar todos los registros desde CSVs")

    args = parser.parse_args()

    if args.test:
        generar_certificado_prueba()
    elif args.todos:
        procesar_csvs_y_generar_certificados(max_registros_test=None)
    else:
        print("No se especificó ninguna opción. Usá --help para ver opciones.")