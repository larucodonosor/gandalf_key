import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

INDEX_PATH = "config/index.json"


def update_index(local_path, drive_id):
    index = {}
    # 1. Carga el índice actual
    if os.path.exists(INDEX_PATH):
            try:
                with open(INDEX_PATH, 'r') as f:
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
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        with open(INDEX_PATH, 'w') as f:
            json.dump(index, f, indent=4)
        logger.info(f" Index actualizado: {os.path.basename(local_path)}")
    except Exception as e:
        logger.error(f" Error guardando index: {e}")

def get_drive_id(local_path):
    # Recupera el ID para una ruta de archivo local determinada.
    if not os.path.exists(INDEX_PATH):
        return None

    try:
        with open(INDEX_PATH, 'r') as f:
            index = json.load(f)
            return index.get(local_path, {}).get("drive_id")
    except Exception:
        logger.error(f" Error al obtener drive_id: {local_path}")
        return None
