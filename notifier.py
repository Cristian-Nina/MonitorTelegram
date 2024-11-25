import os
import json
import time
import asyncio
from telethon import TelegramClient

# Cargar configuraciones desde config.json
config_path = r"C:\Users\crism\OneDrive\Desktop\PROYECTOS\TERMINADO\telegram monitor\config.json"
with open(config_path, "r") as config_file:
    config = json.load(config_file)

bot_token = config.get("BOT_TOKEN")
api_id = config.get("TELEGRAM_API_ID")
api_hash = config.get("TELEGRAM_API_HASH")
channel = config.get("TELEGRAM_CHANNEL")

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

# Diccionario para rastrear líneas procesadas por archivo
processed_lines = {}

# Función para enviar un mensaje al canal de Telegram
async def send_to_telegram(client, channel, file_data):
    try:
        await client.send_message(channel, file_data)
        print(f"Mensaje enviado a {channel}.")
    except Exception as e:
        print(f"Error enviando mensaje a {channel}: {e}")

# Función para procesar archivos y enviar líneas nuevas
async def process_files(client, matched_folder, channel):
    while True:
        try:
            # Obtener la lista de archivos en la carpeta
            files = [f for f in os.listdir(matched_folder) if f.endswith("_matched.txt")]

            for file_name in files:
                file_path = os.path.join(matched_folder, file_name)

                # Inicializar el registro si el archivo es nuevo
                if file_name not in processed_lines:
                    processed_lines[file_name] = 0

                # Leer las líneas nuevas del archivo
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()

                new_lines = lines[processed_lines[file_name]:]  # Obtener solo las líneas nuevas

                if new_lines:
                    # Crear el JSON para las líneas nuevas
                    file_data = {
                        "canal_origen": file_name.split("_matched")[0],
                        "archivo": file_name,
                        "credenciales_nuevas": [line.strip() for line in new_lines],
                    }

                    # Enviar el JSON al canal de Telegram
                    await send_to_telegram(client, channel, json.dumps(file_data, indent=2))

                    # Actualizar el número de líneas procesadas
                    processed_lines[file_name] += len(new_lines)
                    print(f"Líneas nuevas procesadas en {file_name}: {len(new_lines)}")

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
    await process_files(client, matched_folder, channel)

if __name__ == "__main__":
    print("Iniciando script...")
    asyncio.run(main())
