import json
import os
from datetime import datetime
import sys
import logging

logger = logging.getLogger(__name__)

# Estandariza las rutas tanto para desarrollo como producción
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CONFIG_DIR = os.path.join(_BASE_DIR, 'config')
os.makedirs(_CONFIG_DIR, exist_ok=True)

# Variable global
_INDEX_PATH = os.path.join(_CONFIG_DIR, "index.json")

def update_index(local_path, drive_id):
    index = {}
    # 1. Carga el índice actual
    if os.path.exists(_INDEX_PATH):
            try:
                with open(_INDEX_PATH, 'r') as f:
                    index = json.load(f)
            except json.JSONDecodeError:
                index = {}
    else:
        index = {}

    # 2. Actualiza la entrada con ID y fecha
    # Usa un diccionario anidado para poder guardar más datos en el futuro
    index[local_path] = {
        "drive_id": drive_id,
        "last_sync": datetime.now().isoformat()
    }

    # 3. Guardar con verificación de directorio
    try:
        os.makedirs(os.path.dirname(_INDEX_PATH), exist_ok=True)
        with open(_INDEX_PATH, 'w') as f:
            json.dump(index, f, indent=4)
        logger.info(f" Index actualizado: {os.path.basename(local_path)}")
    except Exception as e:
        logger.error(f" Error guardando index: {e}")

def get_index_file_path():
    # Devuelve la ruta absoluta del archivo index.json.
    return _INDEX_PATH

def get_drive_id(local_path):
    # Recupera el ID para una ruta de archivo local determinada.
    if not os.path.exists(_INDEX_PATH):
        return None

    try:
        with open(_INDEX_PATH, 'r') as f:
            index = json.load(f)
            return index.get(local_path, {}).get("drive_id")
    except Exception:
        logger.error(f" Error al obtener drive_id: {local_path}")
        return None
