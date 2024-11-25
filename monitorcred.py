from telethon.sync import TelegramClient
from telethon.tl.types import Document
from telethon import events
import os
import json
import asyncio

# Cargar las credenciales desde el archivo config.json
with open(r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\config.json", "r") as config_file:
    config = json.load(config_file)

api_id = config["TELEGRAM_API_ID"]
api_hash = config["TELEGRAM_API_HASH"]
phone_number = config["TELEGRAM_PHONE_NUMBER"]

channel_file_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\channels.txt"

# Función para leer los canales y grupos desde el archivo
def read_channels_and_groups():
    with open(channel_file_path, 'r') as channel_file:
        return channel_file.read().splitlines()

# Inicializar la lista de canales y grupos
channels_and_groups = read_channels_and_groups()

# Función para descargar archivos
async def download_file(client, message, download_directory):
    try:
        # Diagnóstico: Mostrar información del archivo
        print(f"Intentando descargar archivo: {message.file.name} con MIME: {message.file.mime_type}")
        
        file_path = await client.download_media(message, file=download_directory)
        print(f"Archivo descargado: {file_path}")
    except Exception as e:
        print(f"Error descargando archivo: {e}")

# Manejar mensajes nuevos en tiempo real
async def handle_new_message(event, client, download_directory):
    try:
        # Diagnóstico: Verificar si el mensaje tiene un documento
        if event.message.document and isinstance(event.message.document, Document):
            print("Se detectó un documento adjunto.")

            # Verificar si es un archivo de texto plano
            if event.message.document.mime_type == 'text/plain':
                print("El archivo es de tipo texto.")

                sender = await event.get_chat()
                # Usar el username o el title del canal, dependiendo de lo que esté disponible
                channel_or_group = sender.username if sender.username else sender.title
                # Limpiar cualquier espacio adicional
                channel_or_group = channel_or_group.strip().lower()

                print(f"Mensaje proveniente de: {channel_or_group}")

                # Verificar si el mensaje proviene de los canales/grupos configurados
                if any(channel_or_group == channel.strip().lower() for channel in channels_and_groups):
                    print(f"Canal permitido: {channel_or_group}. Procesando descarga...")
                    await download_file(client, event.message, download_directory)
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
    # Iniciar una sesión con tu cuenta
    async with TelegramClient(phone_number, api_id, api_hash) as client:
        print("¡Cliente iniciado exitosamente!")
        
        # Crear un directorio para guardar los archivos descargados
        download_directory = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\leaks"
        os.makedirs(download_directory, exist_ok=True)

        # Registrar los canales y manejar mensajes nuevos
        @client.on(events.NewMessage)
        async def new_message_listener(event):
            await handle_new_message(event, client, download_directory)

        print("Monitoreando mensajes en tiempo real...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    print("Iniciando el script...")
    asyncio.run(main())
