import json
import os
from dotenv import load_dotenv

load_dotenv()
MASTER_KEY = os.getenv("MASTER_KEY")
DB_USB = "known_devices.json"

def ensure_db_file():
    # Crea el archivo si no existe
    if not os.path.exists(DB_USB):
        with open(DB_USB, "w") as f:
            json.dump([], f)
        print(f" Base de datos {DB_USB} creada correctamente.")

def load_known_devices():
    ensure_db_file()
    try:
        with open(DB_USB, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def is_usb_authorized(id_usb):
    return id_usb in load_known_devices()

def authorize_neww_usb(usb_id, provided_key):
    # Verifica la llave maestra antes de guardar
    if provided_key == MASTER_KEY:
        known_devices = load_known_devices()
        if usb_id not in known_devices:
            known_devices.append(usb_id)
            with open(DB_USB, "w") as f:
                json.dump(known_devices, f, indent=4)
        return True, " USB Autorizado con éxito."
    return False, " Clave incorrecta. Acceso denegado."