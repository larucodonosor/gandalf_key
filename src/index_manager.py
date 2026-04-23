import json
import os
from datetime import datetime

INDEX_PATH = "config/index.json"


def update_index(filename, file_id):
    # 1. Carga el índice actual
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, 'r') as f:
            try:
                index = json.load(f)
            except json.JSONDecodeError:
                index = {}
    else:
        index = {}

    # 2. Actualiza la entrada con ID y fecha
    # Usa un diccionario anidado para poder guardar más datos en el futuro
    index[filename] = {
        "file_id": file_id,
        "last_updated": datetime.now().isoformat()
    }

    # 3. Guardar
    with open(INDEX_PATH, 'w') as f:
        json.dump(index, f, indent=4)