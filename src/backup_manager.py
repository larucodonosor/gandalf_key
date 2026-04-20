import hashlib
import json
import os


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
    # Calcula el SHA-256 hash paraa detectar cambios en el contenido.
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error calculating hash: {e}")
        return None


def analyze_file(file_path):
    # Decide si el archivo requiere la realización de un backup
    if not is_treasure_extension(file_path):
        return False, "Not a treasure file"

    hashed_file = get_file_hash(file_path)

    if hashed_file:
        print(f"✅ File validated: {file_path}")
        print(f"🔍 Hash generated: {hashed_file}")
        return True, hashed_file

    return False, "Error processing hash"