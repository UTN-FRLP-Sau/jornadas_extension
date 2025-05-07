import os
import pandas as pd
import re

def limpiar_nombre_charla(nombre_archivo):
    """Formatea el nombre de la charla."""
    nombre = os.path.splitext(nombre_archivo)[0]
    nombre = nombre.replace('(respuestas)', '').strip()
    return nombre

def validar_y_limpiar_csv(path_csv):
    """
    Lee un CSV, valida y limpia registros.
    Devuelve: df_clean, df_errors.
    """
    df = pd.read_csv(path_csv, dtype=str).fillna('')

    clean_rows = []
    error_rows = []

    email_pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')

    for idx, row in df.iterrows():
        errors = []
        # Trim
        apellido = row['Apellido'].strip().title()
        nombre   = row['Nombre'].strip().title()
        dni      = row['DNI'].strip()
        legajo   = row['Legajo'].strip()
        mail     = row['Mail'].strip()

        # Validaciones
        if not dni.isnumeric():
            errors.append("DNI no numérico")
        if not legajo.isnumeric():
            errors.append("Legajo no numérico")
        if not email_pattern.match(mail):
            errors.append("Mail formato inválido")

        if errors:
            # Registro con fallo: guardamos todos los campos + motivo
            error_rows.append({
                'Fila': idx + 1,
                'Apellido': row['Apellido'],    # valores originales
                'Nombre': row['Nombre'],
                'DNI': row['DNI'],
                'Legajo': row['Legajo'],
                'Mail': row['Mail'],
                'Errores': "; ".join(errors)
            })
        else:
            # Registro limpio
            clean_rows.append({
                'Apellido': apellido,
                'Nombre': nombre,
                'DNI': int(dni),
                'Legajo': int(legajo),
                'Mail': mail
            })

    df_clean  = pd.DataFrame(clean_rows)
    df_errors = pd.DataFrame(error_rows)
    return df_clean, df_errors

def agrupar_por_dominio(df):
    """Agrupa los correos por dominio y devuelve un DataFrame con el conteo."""
    df['Dominio'] = df['Mail'].apply(lambda x: x.split('@')[1] if isinstance(x, str) else x)
    agrupado = df.groupby('Dominio').agg({'Mail': 'count'}).rename(columns={'Mail': 'Conteo'}).reset_index()
    return agrupado

def procesar_csv(departamento, archivo_csv):
    """Procesa un archivo CSV de una charla en un departamento."""
    # Obtener el nombre de la charla
    nombre_charla = limpiar_nombre_charla(archivo_csv)

    # Leer el CSV original
    path_csv = os.path.join(departamento, archivo_csv)

    # Limpiar y validar los datos
    df_clean, df_errors = validar_y_limpiar_csv(path_csv)

    # Crear la carpeta de salida si no existe
    salida_dir = os.path.join(departamento, 'inscripciones-limpias')
    if not os.path.exists(salida_dir):
        os.makedirs(salida_dir)

    # Nombre base para los archivos
    base = nombre_charla.replace(" ", "_")

    # Guardar los registros limpios
    archivo_limpio = os.path.join(salida_dir, f'limpio_{base}.csv')
    df_clean.to_csv(archivo_limpio, index=False)

    # Guardar los registros con errores, si existen
    archivo_errores = None
    if not df_errors.empty:
        archivo_errores = os.path.join(salida_dir, f'errores_{base}.csv')
        df_errors.to_csv(archivo_errores, index=False)

    # Agrupar mails por dominio y guardar
    agrupacion = agrupar_por_dominio(df_clean)
    archivo_dominios = os.path.join(salida_dir, f'dominios_{base}.csv')
    agrupacion.to_csv(archivo_dominios, index=False)

    return archivo_limpio, archivo_errores, archivo_dominios

def procesar_departamentos(directorio_base):
    """Procesa todos los archivos CSV en el directorio base."""
    for departamento in os.listdir(directorio_base):
        departamento_path = os.path.join(directorio_base, departamento)
        if os.path.isdir(departamento_path):
            for archivo_csv in os.listdir(departamento_path):
                if archivo_csv.endswith('.csv'):
                    archivo_limpio, archivo_errores, archivo_dominios = procesar_csv(departamento_path, archivo_csv)
                    print(f"✅ Archivo limpio guardado en: {archivo_limpio}")
                    if archivo_errores:
                        print(f"⚠️  Errores guardados en: {archivo_errores}")
                    print(f"📊 Agrupación de dominios guardada en: {archivo_dominios}")

if __name__ == '__main__':
    # Directorio base donde se encuentran las carpetas 'inscripciones' y 'inscripciones-limpias'
    directorio_base = os.path.join(os.path.dirname(__file__), '..', 'inscripciones')  # Ruta desde 'scripts'
    
    # Procesar los departamentos y archivos CSV
    procesar_departamentos(directorio_base)
