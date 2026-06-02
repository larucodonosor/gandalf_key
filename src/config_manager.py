import json
import os
import sys
import logging

logger = logging.getLogger(__name__)

# Estandariza las rutas para validarlas tanto en desarrolllo como en producción.
def get_secure_config_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, CONFIG_FILE)

CONFIG_FILE = "config_user.json"

def load_config():
    config_path = get_secure_config_path()
    if not os.path.exists(config_path):
        logger.info(f"No se encontró archivo de configuración. Generando plantilla base en: {config_path}")
        # Configuración por defecto si no existe
        default_config = {"backup": {"enabled": True, "days": ["tuesday", "friday"], "time": "03:00", "retention_days": 30}}
        keep_config(default_config)
        return default_config

    with open(config_path, "r") as f:
        return json.load(f)

def keep_config(new_config):
    config_path = get_secure_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump(new_config, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        logger.info(f"Configuración guardada correctamente en: {os.path.abspath(config_path)}.")
        print(f"Configuración guardada correctamente en: {os.path.abspath(config_path)}.")
    except Exception as e:
        logger.error(f"Error crítico al intentar guardar la configuración: {e}")
        raise e