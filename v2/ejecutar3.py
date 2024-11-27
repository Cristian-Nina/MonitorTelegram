import os
import json
import time
import asyncio
import re
from telethon import TelegramClient

# Cargar configuraciones desde config.json
config_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\config.json"
with open(config_path, "r") as config_file:
    config = json.load(config_file)

bot_token = config.get("BOT_TOKEN")
api_id = config.get("TELEGRAM_API_ID")
api_hash = config.get("TELEGRAM_API_HASH")
channel = config.get("TELEGRAM_CHANNEL")

# Ruta del archivo downloads.json
downloads_json_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\downloads.json"

# Preguntar por el canal si no está definido
if not channel:
    user_input = input("Por favor, ingresa el nombre del canal o enlace (por ejemplo, credtest o https://t.me/credtest): ").strip()
    if user_input.startswith("https://t.me/"):  # Extraer el nombre del canal si es un enlace
        channel = user_input.split("/")[-1]
    else:
        channel = user_input

    # Asegurarse de que el nombre del canal tenga "@" al inicio
    if not channel.startswith("@"):
        channel = "@" + channel

# Ruta de la carpeta matched
matched_folder = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\matched"

# Ruta de registro de archivos procesados
processed_log_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\matched\processed_files.json"

# Diccionario para rastrear líneas procesadas por archivo
processed_lines = {}

# Función para enviar un mensaje al canal de Telegram
async def send_to_telegram(client, channel, file_data):
    try:
        await client.send_message(channel, file_data)
        print(f"Mensaje enviado a {channel}.")
    except Exception as e:
        print(f"Error enviando mensaje a {channel}: {e}")

# Función para obtener los archivos ya procesados desde el log
def get_processed_files():
    if os.path.exists(processed_log_path):
        with open(processed_log_path, "r", encoding="utf-8") as log_file:
            return set(json.load(log_file))
    else:
        return set()

# Función para agregar un archivo al registro de archivos procesados
def add_to_processed_log(file_name):
    processed_files = get_processed_files()
    processed_files.add(file_name)
    with open(processed_log_path, "w", encoding="utf-8") as log_file:
        json.dump(list(processed_files), log_file, indent=2)

# Función para procesar archivos y enviar líneas nuevas
async def process_files(client, matched_folder, channel, downloads_json_path):
    processed_files = get_processed_files()  # Obtener archivos ya procesados del log
    while True:
        try:
            # Leer el archivo downloads.json
            with open(downloads_json_path, "r", encoding="utf-8") as json_file:
                downloads_data = json.load(json_file)

            print(f"Datos de {downloads_json_path} cargados correctamente.")

            # Obtener la lista de archivos .txt en la carpeta matched
            files = [f for f in os.listdir(matched_folder) if f.endswith(".txt")]
            if not files:
                print(f"No se encontraron archivos .txt en {matched_folder}")
            else:
                print(f"Archivos encontrados: {files}")

            for file_name in files:
                if file_name in processed_files:
                    print(f"Archivo {file_name} ya procesado. Saltando.")
                    continue  # Saltar archivos ya procesados

                file_path = os.path.join(matched_folder, file_name)

                # Inicializar el registro si el archivo es nuevo
                if file_name not in processed_lines:
                    processed_lines[file_name] = 0

                # Leer las líneas nuevas del archivo
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()

                new_lines = lines[processed_lines[file_name]:]  # Obtener solo las líneas nuevas

                if new_lines:
                    # Buscar el canal y el timestamp en downloads.json
                    for record in downloads_data:
                        if record["file_name"] == file_name:
                            channel_or_group = record["channel_or_group"]
                            timestamp = record["timestamp"]

                            # Crear la estructura del mensaje con las credenciales
                            credentials = []
                            for line in new_lines:
                                line = line.strip()  # Eliminar espacios en blanco al inicio y final
                                # Usar regex para dividir correctamente por los últimos dos ":", excepto para la URL
                                match = re.match(r"^(.*):([^:]+):([^:]+)$", line)  # Esto captura todo hasta el último ":" como URL
                                if match:
                                    url, usuario, contrasena = match.groups()
                                    credentials.append({
                                        "url": url.strip(),  # Eliminar espacios extra
                                        "user": usuario.strip(),
                                        "pass": contrasena.strip()
                                    })
                                else:
                                    print(f"Línea no válida (formato incorrecto): {line}")  # Depuración: línea no válida

                            # Verificación: si hay credenciales, creamos el mensaje
                            if credentials:
                                file_data = {
                                    "channel_or_group": channel_or_group,
                                    "file_name": file_name,
                                    "timestamp": timestamp,
                                    "credentials": credentials
                                }

                                # Enviar el JSON al canal de Telegram
                                await send_to_telegram(client, channel, json.dumps(file_data, indent=2))

                                # Actualizar el número de líneas procesadas
                                processed_lines[file_name] += len(new_lines)
                                print(f"Líneas nuevas procesadas en {file_name}: {len(new_lines)}")

                                # Registrar el archivo como procesado
                                add_to_processed_log(file_name)
                                processed_files.add(file_name)

        except Exception as e:
            print(f"Error procesando archivos: {e}")

        # Esperar 10 segundos antes de volver a verificar
        await asyncio.sleep(10)

# Función principal
async def main():
    print("Iniciando bot de Telegram...")
    client = TelegramClient("bot_session", api_id, api_hash)
    await client.start(bot_token=bot_token)
    print(f"Bot iniciado y monitoreando la carpeta: {matched_folder}")
    await process_files(client, matched_folder, channel, downloads_json_path)

if __name__ == "__main__":
    print("Iniciando script...")
    asyncio.run(main())
