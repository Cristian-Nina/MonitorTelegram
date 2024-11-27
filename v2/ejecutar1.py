from telethon.sync import TelegramClient
from telethon.tl.types import Document
from telethon import events
import os
import json
import asyncio
from datetime import datetime

# Cargar las credenciales desde el archivo config.json
with open(r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\config.json", "r") as config_file:
    config = json.load(config_file)

api_id = config["TELEGRAM_API_ID"]
api_hash = config["TELEGRAM_API_HASH"]
phone_number = config["TELEGRAM_PHONE_NUMBER"]

channel_file_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\channels.txt"
log_file_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\downloads.json"

# Función para leer los canales y grupos desde el archivo
def read_channels_and_groups():
    with open(channel_file_path, 'r') as channel_file:
        return channel_file.read().splitlines()

# Inicializar la lista de canales y grupos
channels_and_groups = read_channels_and_groups()

# Función para actualizar el archivo JSON con los registros de descargas
def update_download_log(channel_or_group, file_name):
    try:
        # Verificar si el archivo de registro existe, si no, crear uno vacío
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as log_file:
                json.dump([], log_file, indent=4)

        # Leer los registros actuales
        with open(log_file_path, 'r') as log_file:
            logs = json.load(log_file)

        # Crear un nuevo registro
        new_entry = {
            "channel_or_group": channel_or_group,
            "file_name": file_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Agregar el nuevo registro y guardar el archivo
        logs.append(new_entry)
        with open(log_file_path, 'w') as log_file:
            json.dump(logs, log_file, indent=4)

        print(f"Registro añadido al log: {new_entry}")
    except Exception as e:
        print(f"Error actualizando el log de descargas: {e}")

# Función para descargar archivos
async def download_file(client, message, download_directory, channel_or_group):
    try:
        temp_file_path = os.path.join(download_directory, f"{message.file.name}.partial")
        final_file_path = os.path.join(download_directory, message.file.name)

        print(f"Descargando archivo temporal: {temp_file_path}")
        file_path = await client.download_media(message, file=temp_file_path)
        os.rename(temp_file_path, final_file_path)
        print(f"Archivo final renombrado a: {final_file_path}")

        # Registrar la descarga en el archivo JSON
        update_download_log(channel_or_group, message.file.name)
    except Exception as e:
        print(f"Error descargando archivo: {e}")

# Manejar mensajes nuevos en tiempo real
async def handle_new_message(event, client, download_directory):
    try:
        if event.message.document and isinstance(event.message.document, Document):
            if event.message.document.mime_type == 'text/plain':
                sender = await event.get_chat()
                channel_or_group = sender.username if sender.username else sender.title
                channel_or_group = channel_or_group.strip().lower()

                if any(channel_or_group == channel.strip().lower() for channel in channels_and_groups):
                    print(f"Canal permitido: {channel_or_group}. Procesando descarga...")
                    await download_file(client, event.message, download_directory, channel_or_group)
                else:
                    print(f"Canal no autorizado: {channel_or_group}")
            else:
                print(f"Archivo con MIME no compatible: {event.message.document.mime_type}")
        else:
            print("El mensaje no contiene un documento.")
    except Exception as e:
        print(f"Error manejando mensaje nuevo: {e}")

async def main():
    print("Iniciando cliente de Telegram...")
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        print("¡Cliente iniciado exitosamente!")
        
        download_directory = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\leaks"
        os.makedirs(download_directory, exist_ok=True)

        @client.on(events.NewMessage)
        async def new_message_listener(event):
            await handle_new_message(event, client, download_directory)

        print("Monitoreando mensajes en tiempo real...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    print("Iniciando el script...")
    asyncio.run(main())
