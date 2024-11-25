import os
import chardet
import time

def load_domains(domain_file_path):
    """Cargar los dominios desde un archivo txt."""
    try:
        with open(domain_file_path, 'r', encoding='utf-8') as f:
            domains = f.read().splitlines()  # Leer los dominios línea por línea
        return domains
    except Exception as e:
        print(f"Error loading domains: {e}")
        return []

def analyze_txt(file_path, domains, matched_folder):
    found_lines = []  # Lista para almacenar las líneas que coincidan con los dominios
    try:
        # Detectar la codificación del archivo
        with open(file_path, 'rb') as raw_file:
            raw_data = raw_file.read()
            encoding = chardet.detect(raw_data)['encoding']

        # Abrir el archivo con la codificación detectada
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()  # Leer todas las líneas del archivo

        # Buscar cada línea por los dominios
        for line in lines:
            for domain in domains:
                if domain in line:  # Si el dominio se encuentra en la línea
                    found_lines.append(line)  # Añadir la línea a la lista

        # Si se encuentran coincidencias, guardarlas en un archivo nuevo
        if found_lines:
            # Crear la ruta completa para el archivo de salida en la carpeta "matched"
            output_file_path = os.path.join(matched_folder, os.path.basename(file_path).replace('.txt', '_matched.txt'))
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.writelines(found_lines)  # Escribir las líneas encontradas

            print(f"Matched lines saved to {output_file_path}")
        else:
            print(f"No matches found in {file_path}")

        # Eliminar el archivo original después de procesarlo
        os.remove(file_path)
        print(f"Deleted {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def monitor_leaks_folder(leaks_folder, domain_file_path, matched_folder):
    # Cargar los dominios desde el archivo
    domains = load_domains(domain_file_path)
    
    if not domains:
        print("No domains to search for. Exiting...")
        return

    # Crear la carpeta de resultados si no existe
    if not os.path.exists(matched_folder):
        os.makedirs(matched_folder)

    # Monitorear la carpeta 'leaks/' para analizar los archivos .txt
    print("Monitoring leaks folder for new files...")
    while True:
        # Lista los archivos en la carpeta leaks
        files_in_leaks = [f for f in os.listdir(leaks_folder) if f.endswith('.txt')]

        # Procesar los archivos nuevos
        for file_name in files_in_leaks:
            file_path = os.path.join(leaks_folder, file_name)
            if os.path.isfile(file_path):  # Verificar si el archivo sigue existiendo
                print(f"Processing {file_path}...")
                analyze_txt(file_path, domains, matched_folder)

        # Esperar un tiempo antes de volver a revisar
        time.sleep(10)  # Espera de 10 segundos antes de la siguiente revisión

# Directorio de los archivos de filtraciones y el archivo de dominios
leaks_folder = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\leaks"
domain_file_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\domains.txt"
matched_folder = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\matched"  # Carpeta donde se guardarán los archivos con coincidencias

# Ejecutar la función principal
monitor_leaks_folder(leaks_folder, domain_file_path, matched_folder)
