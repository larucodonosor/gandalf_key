import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json

logger = logging.getLogger(__name__)

CONFIG_FILE = "config_user.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        # Configuración por defecto si no existe
        return {"backup": {"enabled": True, "days": ["tuesday", "friday"], "time": "03:00"}}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def keep_config(nueva_config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(nueva_config, f, indent=4)

# Configuración básica
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(days_to_keep):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    # Define el formato
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # when='D': Rota cada día
    # interval=1: Rota cada día
    # backupCount=days_to_keep: Mantiene según elección del user los antiguos.
    # 2. Handler para HISTORIAL (Todo menos red)
    history_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "historial.log"),
        when="D", interval=1, backupCount=days_to_keep
    )
    history_handler.setFormatter(formatter)
    # Filtro: Solo deja pasar si NO es del módulo de red
    history_handler.addFilter(lambda record: "network_utils" not in record.name)
    root_logger.addHandler(history_handler)

    # 3. Handler para RED (Solo network_utils)
    network_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "network_activity.log"),
        when="D", interval=1, backupCount=days_to_keep
    )
    network_handler.setFormatter(formatter)
    # Filtro: Solo deja pasar si el nombre es exactamente el de red
    network_handler.addFilter(lambda record: "network_utils" in record.name)
    root_logger.addHandler(network_handler)

    logger.info('Sistema de logs iniciado correctamente')


