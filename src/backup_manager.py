import hashlib
import json
import os
import index_manager
import cloud_vault
from datetime import datetime


def load_config():
    # Carga el archivo 'treasures.json'.
    with open("config/treasures.json", "r") as f:
        return json.load(f)


def is_treasure_extension(file_path):
    # Comprueba si una extensión se encuentra en la lista.
    config = load_config()
    # Lista de extensions -> las engloba en una variable
    valid_extensions = [ext for sublist in config["treasure_types"].values() for ext in sublist]
    return file_path.endswith(tuple(valid_extensions))


def get_file_hash(file_path):
    # Calcula el SHA-256 hash para detectar cambios en el contenido.
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error calculating hash: {e}")
        return None

def needs_backup(file_path):
    # Compara fecha local vs fecha en el índice.
    if not os.path.exists(file_path):
        return False

    # Obtiene tiempo local
    local_mtime = os.path.getmtime(file_path)

    if os.path.exists("config/index.json"):
        with open("config/index.json", 'r') as f:
            index = json.load(f)

        if file_path in index:
            last_backup_time = datetime.fromisoformat(index[file_path].get("last_updated")).timestamp()
            # Si el archivo no ha cambiado desde el último backup, no hacemos nada
            if local_mtime <= last_backup_time:
                return False

                # 2. Validación: ¿Ha cambiado el contenido?

    return True

def run_scheduled_backup(file_list):
    # Punto de entrada para el proceso de backup.
    print(" Iniciando escaneo de cambios...")

    for file_path in file_list:
        # Validación de tipo de archivo
        if not is_treasure_extension(file_path):
            continue

        # Validación de necesidad de backup
        if needs_backup(file_path):
            print(f" Cambio detectado en {file_path}. Procesando...")

            # Genera hash para identificarlo en la nube
            file_hash = get_file_hash(file_path)

            # Subida
            file_id = cloud_vault.upload_to_drive(file_path, file_hash)
            print(f" {file_path} subido con éxito. ID: {file_id}")
        else:
            print(f" {file_path} está actualizado.")
