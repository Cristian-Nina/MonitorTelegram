#!/bin/bash

# Rutas de las carpetas y archivos (actualizadas según lo proporcionado)
LEAKS_FOLDER="/home/administrator/cti/credentials/MonitorTelegram/leaks"
DOMAIN_FILE="/home/administrator/cti/credentials/MonitorTelegram/domains.txt"
MATCHED_FOLDER="/home/administrator/cti/credentials/MonitorTelegram/matched"

# Cargar dominios desde el archivo
domains=()
while IFS= read -r line; do
    domains+=("$line")
done < "$DOMAIN_FILE"

# Crear la carpeta para los archivos coincidentes si no existe
mkdir -p "$MATCHED_FOLDER"

# Función para procesar los archivos
process_file() {
    local file="$1"
    local output_file="$MATCHED_FOLDER/$(basename "$file")"

    # Limpiar el archivo de salida antes de agregar coincidencias
    > "$output_file"

    # Usar grep para buscar las líneas que contienen los dominios
    for domain in "${domains[@]}"; do
        grep -i "$domain" "$file" >> "$output_file" # Añadir las líneas encontradas al archivo de salida
    done

    # Si se encontraron coincidencias, mover el archivo
    if [ -s "$output_file" ]; then
        echo "Matched lines saved to $output_file"
    else
        echo "No matches found in $file"
    fi

    # Eliminar el archivo original después de procesarlo
    rm "$file"
    echo "Deleted $file"
}

# Monitorear la carpeta de filtrado
while true; do
    for file in "$LEAKS_FOLDER"/*.txt; do
        # Procesar solo archivos .txt que no estén en uso (es decir, que no tengan .partial)
        if [ -f "$file" ] && [[ ! "$file" =~ \.partial$ ]]; then
            echo "Processing $file..."
            process_file "$file"
        fi
    done
    sleep 10
done
