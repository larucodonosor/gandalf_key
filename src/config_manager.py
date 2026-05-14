import json
import os
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = "config_user.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        # Configuración por defecto si no existe
        return {"backup": {"enabled": True, "days": ["tuesday", "friday"], "time": "03:00"}}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def keep_config(nueva_config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(nueva_config, f, indent=4)
        logger.info("Configuración guardada correctamente en el disco.")
    except IOError as e:
        logger.error("Error físico al escribir el archivo de configuración: %s", e)
    except Exception as e:
        logger.error(f"Error crítico al intentar guardar la configuración: {e}")
        raise e