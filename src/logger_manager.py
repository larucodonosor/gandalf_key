import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

logger = logging.getLogger(__name__)

# Estandarizado de rutas tanto para desarrollo como para producción
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(_BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

class NetworkFilter(logging.Filter):
    # Deja pasar solo los logs relacionados con red y pasarelas cloud.
    def filter(self, record):
        return "network_utils" in record.name or "telebot" in record.name.lower() or "cloud_vault" in record.name


class HistoryFilter(logging.Filter):
    # Deja pasar todo, excepto los ruidos de conexiones de red.
    def filter(self, record):
        return "network_utils" not in record.name and "telebot" not in record.name.lower() and "cloud_vault" not in record.name

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
    # 1. Handler para HISTORIAL (Todo menos red)
    history_file = os.path.join(LOG_DIR, "historial.log")
    history_handler = TimedRotatingFileHandler(
        history_file, when="D", interval=1, backupCount=days_to_keep, encoding="utf-8"
    )
    history_handler.setFormatter(formatter)
    history_handler.addFilter(HistoryFilter())
    root_logger.addHandler(history_handler)

    # 2. Handler para RED, CLOUD y TELEGRAM
    network_file = os.path.join(LOG_DIR, "network_activity.log")
    network_handler = TimedRotatingFileHandler(
        network_file, when="D", interval=1, backupCount=days_to_keep, encoding="utf-8"
    )
    network_handler.setFormatter(formatter)
    network_handler.addFilter(NetworkFilter())
    root_logger.addHandler(network_handler)

    logger.info('Sistema de logs iniciado correctamente')


