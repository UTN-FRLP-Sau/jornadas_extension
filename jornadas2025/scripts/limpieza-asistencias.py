import pandas as pd
import os

def limpiar_y_formatear_csv(carpeta_csvs='asistencias', subcarpeta_procesadas='procesadas'):
    """
    Limpia los CSVs en la carpeta especificada y los guarda en una subcarpeta 'procesadas':
    1. Elimina espacios al inicio y final de todas las celdas, incluyendo encabezados.
    2. Aplica formato de capitalización (primera letra mayúscula, resto minúsculas)
       a la columna 'Apellido y Nombres'.
    3. Elimina la columna 'Apellido y Nombre legal'.
    Los archivos limpios se guardan en asistencias/procesadas/.
    """
    # Obtener el directorio base donde se encuentra el script
    base_dir = os.path.dirname(os.path.abspath(__file__)) # scripts/
    # Ahora subimos un nivel para llegar a 'tu_proyecto/'
    proyecto_dir = os.path.dirname(base_dir)

    ruta_asistencias = os.path.join(proyecto_dir, carpeta_csvs)
    ruta_procesadas = os.path.join(ruta_asistencias, subcarpeta_procesadas)

    # Crear la subcarpeta 'procesadas' si no existe
    if not os.path.exists(ruta_procesadas):
        os.makedirs(ruta_procesadas)
        print(f"Creada carpeta para CSVs procesados: '{ruta_procesadas}'")

    if not os.path.exists(ruta_asistencias):
        print(f"Error: La carpeta '{ruta_asistencias}' no existe. Asegúrate de que los CSV estén allí.")
        return

    # Listar solo los archivos CSV en la raíz de asistencias (ignorando 'procesadas' para la lectura inicial)
    all_csv_files_in_asistencias = [f for f in os.listdir(ruta_asistencias) if f.endswith('.csv')]
    processed_csv_files = [f for f in os.listdir(ruta_procesadas) if f.endswith('.csv')]
    csv_files_to_process = [f for f in all_csv_files_in_asistencias if f not in processed_csv_files]

    if not csv_files_to_process:
        print(f"No se encontraron nuevos archivos CSV en la carpeta '{ruta_asistencias}' para procesar.")
        return

    print(f"Iniciando limpieza y formato de CSVs en '{ruta_asistencias}' y guardando en '{ruta_procesadas}'...")

    for csv_file in csv_files_to_process:
        csv_path_original = os.path.join(ruta_asistencias, csv_file)
        csv_path_destino = os.path.join(ruta_procesadas, csv_file)
        print(f"\nProcesando archivo: '{csv_file}'")

        try:
            # Leer con delimitador de punto y coma y motor Python
            df = pd.read_csv(csv_path_original, sep=';', engine='python')

            # 1. Limpiar espacios en encabezados
            df.columns = df.columns.str.strip()
            print("  Encabezados limpiados de espacios.")

            # Definir los nombres de columnas esperados para el procesamiento
            COL_APELLIDO_NOMBRES = 'Apellido y Nombres'
            COL_DOCUMENTO = 'Documento'
            COL_MAIL = 'Mail'
            COL_MAIL_UTN = 'Mail UTN'
            COL_APELLIDO_NOMBRE_LEGAL = 'Apellido y Nombre legal' # Columna a eliminar

            # 2. Limpiar espacios en todas las celdas (strings)
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Asegurarse de que los valores sean strings antes de aplicar .strip()
                    df[col] = df[col].astype(str).str.strip()
            print("  Espacios en blanco eliminados de todas las celdas de texto.")

            # 3. Aplicar formato de capitalización a 'Apellido y Nombres'
            if COL_APELLIDO_NOMBRES in df.columns:
                df[COL_APELLIDO_NOMBRES] = df[COL_APELLIDO_NOMBRES].apply(
                    lambda x: ' '.join([name.capitalize() for name in x.split()]) if isinstance(x, str) else x
                )
                print(f"  Formato de capitalización aplicado a '{COL_APELLIDO_NOMBRES}'.")
            else:
                print(f"  Advertencia: Columna '{COL_APELLIDO_NOMBRES}' no encontrada. No se aplicó formato de capitalización.")
                
            # 4. Eliminar la columna 'Apellido y Nombre legal'
            if COL_APELLIDO_NOMBRE_LEGAL in df.columns:
                df = df.drop(columns=[COL_APELLIDO_NOMBRE_LEGAL])
                print(f"  Columna '{COL_APELLIDO_NOMBRE_LEGAL}' eliminada.")
            else:
                print(f"  Advertencia: Columna '{COL_APELLIDO_NOMBRE_LEGAL}' no encontrada. No se eliminó.")


            # Verificar que las columnas clave existan antes de guardar
            if not all(col in df.columns for col in [COL_APELLIDO_NOMBRES, COL_DOCUMENTO, COL_MAIL, COL_MAIL_UTN]):
                print(f"  Advertencia: Faltan una o más columnas esenciales ('{COL_APELLIDO_NOMBRES}', '{COL_DOCUMENTO}', '{COL_MAIL}', '{COL_MAIL_UTN}') después del procesamiento. Archivo '{csv_file}' podría no ser apto para certificados.")


            # Guardar el DataFrame limpio en la subcarpeta 'procesadas'
            df.to_csv(csv_path_destino, index=False, sep=';')
            print(f"  Archivo '{csv_file}' limpiado y guardado exitosamente en '{ruta_procesadas}'.")

        except FileNotFoundError:
            print(f"Error: El archivo '{csv_path_original}' no fue encontrado.")
        except pd.errors.ParserError as e:
            print(f"Error de parsing en '{csv_file}'. El formato del CSV podría ser inconsistente. Detalle: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado al procesar '{csv_file}': {e}")

# --- Ejecución del script ---
if __name__ == "__main__":
    limpiar_y_formatear_csv()
    print("\n¡Proceso de limpieza de CSVs finalizado!")