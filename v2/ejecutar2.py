import os
import chardet
import time

def load_domains(domain_file_path):
    """Cargar los dominios desde un archivo txt."""
    try:
        with open(domain_file_path, 'r', encoding='utf-8') as f:
            domains = f.read().splitlines()
        return domains
    except Exception as e:
        print(f"Error loading domains: {e}")
        return []

def analyze_txt(file_path, domains, matched_folder):
    found_lines = []
    try:
        # Detectar la codificación del archivo
        with open(file_path, 'rb') as raw_file:
            raw_data = raw_file.read()
            encoding = chardet.detect(raw_data)['encoding']

        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()

        for line in lines:
            for domain in domains:
                if domain in line:
                    found_lines.append(line)

        if found_lines:
            # Se conserva el nombre original del archivo
            output_file_path = os.path.join(matched_folder, os.path.basename(file_path))
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.writelines(found_lines)
            print(f"Matched lines saved to {output_file_path}")
        else:
            print(f"No matches found in {file_path}")

        os.remove(file_path)
        print(f"Deleted {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def monitor_leaks_folder(leaks_folder, domain_file_path, matched_folder):
    domains = load_domains(domain_file_path)
    
    if not domains:
        print("No domains to search for. Exiting...")
        return

    if not os.path.exists(matched_folder):
        os.makedirs(matched_folder)

    print("Monitoring leaks folder for new files...")
    while True:
        files_in_leaks = [
            f for f in os.listdir(leaks_folder)
            if f.endswith('.txt') and not f.endswith('.partial')
        ]

        for file_name in files_in_leaks:
            file_path = os.path.join(leaks_folder, file_name)
            if os.path.isfile(file_path):
                print(f"Processing {file_path}...")
                analyze_txt(file_path, domains, matched_folder)

        time.sleep(10)

# Rutas de las carpetas y archivos
leaks_folder = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\leaks"
domain_file_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\domains.txt"
matched_folder = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\matched"

# Iniciar la monitorización
monitor_leaks_folder(leaks_folder, domain_file_path, matched_folder)
