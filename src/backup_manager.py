import hashlib
import json
import os
import sys
import cloud_vault
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Estandariza las rutas tanto para desarrollo como producción
def get_secure_config_path(filename):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if filename == "base_memory.json":
        return os.path.abspath(os.path.join(base_dir, "base_memory.json"))

    config_dir = os.path.join(base_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, filename)

def load_config():
    # Carga el archivo 'treasures.json'.
    treasures_path = get_secure_config_path("treasures.json")

    # Si el archivo no existe aún, crea una plantilla preventiva
    if not os.path.exists(treasures_path):
        default_config = {
            "treasure_types": {
                "documentos": [".pdf", ".docx", ".xlsx", ".txt"],
                "claves": [".key", ".kdbx"]
            }
        }
        with open(treasures_path, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

    with open(treasures_path, "r") as f:
        return json.load(f)

def is_treasure_extension(file_path):
    # Comprueba si una extensión se encuentra en la lista.
    config = load_config()
    # Lista de extensions -> las engloba en una variable
    valid_extensions = [ext for sublist in config["treasure_types"].values() for ext in sublist]
    return file_path.lower().endswith(tuple(valid_extensions))

def get_file_hash(file_path):
    # Calcula el SHA-256 hash para detectar cambios en el contenido.
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash: {e}")
        return None

def needs_backup(file_path):
    # Compara fecha local vs fecha en el índice.
    if not os.path.exists(file_path):
        return False

    # Obtiene tiempo local
    local_mtime = os.path.getmtime(file_path)

    index_path = get_secure_config_path("index.json")

    if os.path.exists(index_path):
        with open(index_path, 'r', encoding="utf-8", errors="replace") as f:
            index = json.load(f)

        if file_path in index:
            last_sync_str = index[file_path].get("last_sync")
            if last_sync_str:
                last_backup_time = datetime.fromisoformat(last_sync_str).timestamp()
                # Si el archivo no ha cambiado desde el último backup, nada
                if local_mtime <= last_backup_time:
                    return False

                # 2. Validación: ¿Ha cambiado el contenido?
    return True

def run_scheduled_backup(file_list):
    # Punto de entrada para el proceso de backup.
    logger.info(" Iniciando escaneo de cambios...")

    for file_path in file_list:
        # Validación de tipo de archivo
        if not is_treasure_extension(file_path):
            continue

        # Validación de necesidad de backup
        if needs_backup(file_path):
            logger.info(f" Cambio detectado en {file_path}. Procesando...")

            # Genera hash para identificarlo en la nube
            file_hash = get_file_hash(file_path)

            # Subida
            file_id = cloud_vault.upload_to_drive(file_path, file_hash)
            logger.info(f" {file_path} subido con éxito. ID: {file_id}")
        else:
            logger.error(f" {file_path} está actualizado.")
