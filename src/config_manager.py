import json
import os
import sys
import logging

logger = logging.getLogger(__name__)

# Standariza las rutas para validarlas tanto en desarrolllo como en producción.
def get_secure_config_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config_user.json")

CONFIG_FILE = "config_user.json"

def load_config():
    config_path = get_secure_config_path()
    if not os.path.exists(config_path):
        logger.info(f"No se encontró archivo de configuración. Generando plantilla base en: {config_path}")
        # Configuración por defecto si no existe
        return {"backup": {"enabled": True, "days": ["tuesday", "friday"], "time": "03:00"}}
    with open(config_path, "r") as f:
        return json.load(f)

def keep_config(new_config):
    config_path = get_secure_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump(new_config, f, indent=4)
        logger.info("Configuración guardada correctamente en el disco.")
    except IOError as e:
        logger.error("Error físico al escribir el archivo de configuración: %s", e)
    except Exception as e:
        logger.error(f"Error crítico al intentar guardar la configuración: {e}")
        raise e