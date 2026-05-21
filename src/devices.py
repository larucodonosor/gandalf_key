import json
import os
import sys
import keyring
import logging

logger = logging.getLogger(__name__)

# Estandariza las rutas tanto para desarrollo como producción
def get_secure_db_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_dir = os.path.join(base_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "known_devices.json")

def ensure_db_file():
    # Crea el archivo si no existe
    db_path = get_secure_db_path()
    if not os.path.exists(db_path):
        with open(db_path, "w") as f:
            json.dump([], f)
        logger.info(f" Base de datos de dispositivos USB creada correctamente en: {db_path}.")

def load_known_devices():
    ensure_db_file()
    db_path = get_secure_db_path()
    try:
        with open(db_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        logger.error(f"Error al leer el archivo de dispositivos USB: {e}")
        return []

def is_usb_authorized(id_usb):
    return id_usb in load_known_devices()

def authorize_new_usb(usb_id, provided_key):
    master_key = keyring.get_password("Gandalf_Guard", "MASTER_KEY")

    if not master_key:
        logger.error("Error de autenticación: No hay ninguna Master Key configurada en el sistema.")
        return False, " Error del sistema: Inicializa la Master Key primero."

    # Verifica la llave maestra antes de guardar
    if provided_key == master_key:
        known_devices = load_known_devices()
        if usb_id not in known_devices:
            known_devices.append(usb_id)
            db_path = get_secure_db_path()
            with open(db_path, "w") as f:
                json.dump(known_devices, f, indent=4)
        return True, " USB Autorizado con éxito."
    logger.warning(f"Intento de autorización de USB denegado. Clave incorrecta.")
    return False, " Clave incorrecta. Acceso denegado."