import os
import pandas as pd
import re

def validar_y_limpiar_csv(path_csv):
    """
    Lee un CSV, valida y limpia registros.
    Devuelve: df_clean, df_errors.
    """
    df = pd.read_csv(path_csv, dtype=str).fillna('')

    # Eliminar espacios en blanco y convierte a minúsculas los nombres de las columnas
    new_columns = []
    for col in df.columns:
        cleaned_col = col.strip().lower()
        new_columns.append(cleaned_col)
    df.columns = new_columns

    # Elimina la columna 'marca temporal'
    if 'marca temporal' in df.columns:
        df = df.drop(columns=['marca temporal'])

    # Mapeo de sinónimos a nombres estándar
    sinonimos_columnas = {
        'correo': 'mail',
        'email': 'mail',
        'e-mail': 'mail',
        'correo electronico': 'mail',
        'correo electrónico': 'mail',
        'apellido y nombre': 'nombre',
    }

    df.columns = [sinonimos_columnas.get(col, col) for col in df.columns]

    clean_rows = []
    error_rows = []

    email_pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')

    for idx, row in df.iterrows():
        errors = []
        # Trim y limpieza
        apellido = row.get('apellido', '').strip().title()
        nombre = row.get('nombre', '').strip().title()
        dni = row.get('dni', '').strip()
        legajo = row.get('legajo', '').strip()
        mail = row.get('mail', '').strip()

        # Formateo dni y legajo
        dni = dni.replace('.', '')  # Elimino puntos del DNI

        legajo = legajo.replace('.', '')  # Elimino puntos del legajo

        # Valido si DNI y legajo son numéricos y el formato del mail
        if dni and not dni.isnumeric():
            errors.append("DNI no numérico")
        
        # Valido el formato del mail (solo letras, números, guiones y puntos permitidos)
        if mail and not email_pattern.match(mail):
            errors.append("Mail formato inválido")

        # Si hubo errores los guardo en error_rows con número de fila y la información del registro
        if errors:
            error_rows.append({
                'Fila': idx + 1,
                'Apellido': row.get('apellido', ''),
                'Nombre': row.get('nombre', ''),
                'DNI': row.get('dni', ''),
                'Legajo': row.get('legajo', ''),
                'Mail': row.get('mail', ''),
                'Errores': "; ".join(errors)
            })
        else: # Si no hay errores, guardo el registro limpio
            clean_rows.append({
                'Apellido': apellido,
                'Nombre': nombre,
                'DNI': dni if dni else None,
                'Legajo': legajo if legajo else None,
                'Mail': mail if mail else None,
            })

    # Creo DataFrames asegurando las columnas
    columnas = ['Apellido', 'Nombre', 'DNI', 'Legajo', 'Mail']
    df_clean = pd.DataFrame(clean_rows, columns=columnas)
    df_errors = pd.DataFrame(error_rows)
    
    return df_clean, df_errors

def agrupar_por_dominio(df):
    """Agrupa los correos por dominio y devuelve un DataFrame con el conteo."""

    if df.empty or 'Mail' not in df.columns:
        print("DataFrame vacío o columna 'Mail' no encontrada. Retornando DataFrame vacío.")
        return pd.DataFrame(columns=['Dominio', 'Conteo'])

    # Filtra mails válidos
    df_mails = df[df['Mail'].notna() & (df['Mail'] != '')].copy()

    if df_mails.empty:
        print("No hay mails válidos después del filtrado. Retornando DataFrame vacío.")
        return pd.DataFrame(columns=['Dominio', 'Conteo'])

    # Extrae dominios
    df_mails['Dominio'] = df_mails['Mail'].str.split('@').str[1]
    agrupado = df_mails.groupby('Dominio').size().reset_index(name='Conteo')

    return agrupado

def procesar_csv(departamento_path, archivo_csv):
    """Procesa un archivo CSV de una charla en un departamento."""
    # Extrae el código de la charla del nombre del archivo (sin extensión)
    nombre_charla = os.path.splitext(archivo_csv)[0]
    
    # Crea estructura de carpetas
    originales_dir = os.path.join(departamento_path, 'originales')
    procesadas_dir = os.path.join(departamento_path, 'procesadas')
    charla_dir = os.path.join(procesadas_dir, nombre_charla)
    
    # Asegura que existan las carpetas necesarias
    os.makedirs(charla_dir, exist_ok=True)

    # Lee el CSV original
    path_csv = os.path.join(originales_dir, archivo_csv)

    # Limpia y valida los datos
    df_clean, df_errors = validar_y_limpiar_csv(path_csv)

    # Guarda los archivos procesados
    archivo_limpio = os.path.join(charla_dir, f'{nombre_charla}.csv')
    df_clean.to_csv(archivo_limpio, index=False)

    archivo_errores = os.path.join(charla_dir, 'errores.csv')
    df_errors.to_csv(archivo_errores, index=False)

    agrupacion = agrupar_por_dominio(df_clean)
    archivo_dominios = os.path.join(charla_dir, 'dominios.csv')
    agrupacion.to_csv(archivo_dominios, index=False)

    return archivo_limpio, archivo_errores, archivo_dominios

def procesar_inscripciones(directorio_base):
    """Procesa todos los archivos CSV en el directorio base."""
    # Recorro carpeta inscripciones
    for departamento in os.listdir(directorio_base):
        # Construye la ruta completa al directorio del departamento
        departamento_path = os.path.join(directorio_base, departamento)
        

        if os.path.isdir(departamento_path):
            # Construye la ruta al directorio 'originales' dentro del departamento
            originales_dir = os.path.join(departamento_path, 'originales')
            # Verifica si existe el directorio 'originales'
            if not os.path.exists(originales_dir):
                print(f"⚠️ No se encontró la carpeta 'originales' en {departamento}")
                continue # Pasa al siguiente departamento si no existe 'originales'
            
            # Construye la ruta al directorio 'procesadas' dentro del departamento
            procesadas_dir = os.path.join(departamento_path, 'procesadas')
            # Crea el directorio 'procesadas' si no existe
            os.makedirs(procesadas_dir, exist_ok=True)
            
            # Recorro los csv originales
            for archivo_csv in os.listdir(originales_dir):
                if archivo_csv.endswith('.csv'):
                    try:
                        # Procesa el archivo CSV y obtiene las rutas de los archivos generados
                        archivo_limpio, archivo_errores, archivo_dominios = procesar_csv(departamento_path, archivo_csv)
                        
                        print(f"✅ Procesado {archivo_csv} en {departamento}")
                        print(f"  - Datos limpios: {archivo_limpio}")
                        
                        # Obtiene el tamaño del archivo de errores
                        errores_size = os.path.getsize(archivo_errores) if os.path.exists(archivo_errores) else 0
                        # Imprime la ruta del archivo de errores si su tamaño es mayor a 50 bytes (umbral para considerar que contiene errores)
                        if errores_size > 50:  # Umbral mayor que solo headers
                            print(f"  - Errores encontrados: {archivo_errores}")
                        else:
                            print("  - No se encontraron errores")
                        
                        # Ruta de dominios procesados
                        print(f"  - Dominios procesados: {archivo_dominios}")
                        
                    # Captura cualquier excepción que ocurra durante el procesamiento del archivo
                    except Exception as e:
                        # Imprime un mensaje de error con la descripción de la excepción
                        print(f"❌ Error procesando {archivo_csv} en {departamento}: {str(e)}")


if __name__ == '__main__':
    # Directorio base donde se encuentran las carpetas de departamentos
    directorio_base = os.path.join(os.path.dirname(__file__), '..', 'inscripciones')

    # Procesa las inscripciones
    procesar_inscripciones(directorio_base)