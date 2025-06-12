import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from datetime import date

def generar_certificado(nombre_completo, documento, mail, ruta_salida_pdf):
    """
    Genera un certificado de asistencia en PDF con los datos proporcionados.
    """
    c = canvas.Canvas(ruta_salida_pdf, pagesize=letter)
    width, height = letter

    # --- Contenido del Certificado ---

    # Título
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - 1.5 * inch, "Certificado de Asistencia")

    # Texto principal
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 2.5 * inch, "La Universidad Tecnológica Nacional - Facultad Regional La Plata")
    c.drawCentredString(width / 2.0, height - 2.8 * inch, "certifica que:")

    # Nombre del alumno
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2.0, height - 3.5 * inch, nombre_completo)

    # Documento
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2.0, height - 4.0 * inch, f"DNI: {documento}")

    # Mail
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2.0, height - 4.3 * inch, f"Email: {mail}")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 5.5 * inch, "Ha participado exitosamente en las Jornadas de Extensión Universitaria.")
    c.drawCentredString(width / 2.0, height - 5.8 * inch, "Celebradas en la institución.")

    # Fecha de Emisión (se asume que la fecha de emisión del certificado es hoy)
    # Nombre de los meses en español para la fecha dinámica
    meses_espanol = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    fecha_actual = date.today()
    c.setFont("Helvetica", 10)
    c.drawString(1.0 * inch, 1.5 * inch, f"Fecha de Emisión: {fecha_actual.day} de {meses_espanol[fecha_actual.month - 1]} de {fecha_actual.year}")
    c.drawString(1.0 * inch, 1.2 * inch, "Berisso, Buenos Aires, Argentina")

    c.save()

# === CAMBIO AQUI: Añadido max_registros_test = 2 ===
def procesar_csvs_y_generar_certificados(carpeta_csvs='asistencias', subcarpeta_origen='procesadas', carpeta_certificados='certificados', max_registros_test=2):
    """
    Procesa los primeros 'max_registros_test' de cada archivo CSV de la subcarpeta 'procesadas',
    genera certificados y los guarda en la estructura de carpetas deseada.
    Establece max_registros_test=None para procesar todos los registros.
    """
    # Obtener el directorio base donde se encuentra el script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    proyecto_dir = os.path.dirname(base_dir)

    ruta_origen_csvs = os.path.join(proyecto_dir, carpeta_csvs, subcarpeta_origen)
    ruta_certificados = os.path.join(proyecto_dir, carpeta_certificados)

    if not os.path.exists(ruta_certificados):
        os.makedirs(ruta_certificados)
        print(f"Creada carpeta principal para certificados: '{ruta_certificados}'")

    if not os.path.exists(ruta_origen_csvs):
        print(f"Error: La carpeta '{ruta_origen_csvs}' no existe. Ejecuta primero el script de limpieza.")
        return

    csv_files = [f for f in os.listdir(ruta_origen_csvs) if f.endswith('.csv')]

    if not csv_files:
        print(f"No se encontraron archivos CSV en la carpeta '{ruta_origen_csvs}'.")
        return

    print(f"Iniciando generación de certificados desde los archivos CSV en '{ruta_origen_csvs}'...")
    if max_registros_test is not None:
        print(f"  (Modo de testeo: procesando solo los primeros {max_registros_test} registros por archivo)")


    for csv_file in csv_files:
        csv_path = os.path.join(ruta_origen_csvs, csv_file)
        
        nombre_subcarpeta = os.path.splitext(csv_file)[0]
        ruta_subcarpeta_certificados = os.path.join(ruta_certificados, nombre_subcarpeta)

        if not os.path.exists(ruta_subcarpeta_certificados):
            os.makedirs(ruta_subcarpeta_certificados)
            print(f"Creada subcarpeta para certificados: '{ruta_subcarpeta_certificados}'")

        try:
            # Leer con delimitador de punto y coma
            df = pd.read_csv(csv_path, sep=';')

            # Definir los nombres de columnas esperados
            COL_APELLIDO_NOMBRES = 'Apellido y Nombres'
            COL_DOCUMENTO = 'Documento'
            COL_MAIL = 'Mail'
            COL_MAIL_UTN = 'Mail UTN'
            
            # Verificar si las columnas esenciales existen
            if not all(col in df.columns for col in [COL_APELLIDO_NOMBRES, COL_DOCUMENTO, COL_MAIL, COL_MAIL_UTN]):
                print(f"Error: Una o más columnas esenciales ('{COL_APELLIDO_NOMBRES}', '{COL_DOCUMENTO}', '{COL_MAIL}', '{COL_MAIL_UTN}') no se encontraron en '{csv_file}'. Saltando este archivo.")
                continue

            if max_registros_test is not None:
                df_procesar = df.head(max_registros_test)
                print(f"  Procesando los primeros {len(df_procesar)} de {len(df)} registros en '{csv_file}'.")
            else:
                df_procesar = df
                print(f"\nProcesando archivo: '{csv_file}' con {len(df_procesar)} registros.")

            for index, row in df_procesar.iterrows(): # Iterar sobre el DataFrame limitado
                apellido_nombre = row[COL_APELLIDO_NOMBRES]
                documento = str(row[COL_DOCUMENTO])
                
                mail_preferido = row[COL_MAIL] if pd.notna(row[COL_MAIL]) else ''
                mail_utn = row[COL_MAIL_UTN] if pd.notna(row[COL_MAIL_UTN]) else ''

                mail_final = mail_preferido if mail_preferido != '' else mail_utn
                
                nombre_limpio = apellido_nombre.replace(" ", "-").replace(",", "").replace(".", "").lower()
                
                nombre_pdf = f"{nombre_limpio}-certificado.pdf"
                ruta_salida_pdf = os.path.join(ruta_subcarpeta_certificados, nombre_pdf)

                generar_certificado(apellido_nombre, documento, mail_final, ruta_salida_pdf)
                print(f"  Generado certificado para '{apellido_nombre}' en '{ruta_salida_pdf}'")

        except FileNotFoundError:
            print(f"Error: El archivo '{csv_path}' no fue encontrado.")
        except KeyError as e:
            print(f"Error: Columna esperada no encontrada en '{csv_file}'. Detalle: {e}. Asegúrate de que los encabezados estén correctos y sin espacios extra.")
        except Exception as e:
            print(f"Ocurrió un error inesperado al procesar '{csv_file}': {e}")

# --- Ejecucion del script ---
if __name__ == "__main__":
    # Para procesar todos los registros poner: max_registros_test=2
    procesar_csvs_y_generar_certificados(max_registros_test=2)

   

    print("\n¡Proceso de generación de certificados finalizado!")