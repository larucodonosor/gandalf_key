import json
import time
import os
import sys
import threading
import schedule
import backup_manager
import logger_manager
import config_manager
import logging

from src.backup_manager import get_secure_config_path

logger = logging.getLogger(__name__)

# Estandariza las rutas  para que sean accesibles tanto en desarrollo como en producción.
def get_secure_state_path(filename):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, filename)

ESTADO_PATH = get_secure_config_path("base_memory.json")

def job_backup():
    config = config_manager.load_config()["backup"]
    if not config["enabled"]:
        return

    # Limpieza de logs antiguos ANTES de hacer nada
    retention_days = config.get("retention_days", 30) # 30 es valor por defecto
    logger_manager.setup_logger(retention_days)

    # Log de inicio del proceso
    logger.info("Iniciando backup programado...")

    try:
        if not os.path.exists(ESTADO_PATH):
            logger.warning(f"No se encontró el archivo de estado {ESTADO_PATH}. Creando uno nuevo vacío.")
            with open(ESTADO_PATH, "w") as f:
                json.dump({}, f)

            with open(ESTADO_PATH, "r") as f:
                estado_actual = json.load(f)

        # Toma la lista de archivos que existen y a backup_manager que tiene la lógica de subida
        files = list(estado_actual.keys())
        backup_manager.run_scheduled_backup(files)
        # Log de éxito
        logger.info(f"Backup finalizado con éxito: {len(files)} archivos procesados.")
    except Exception as e:
        # Log de error (si algo falla, queda registrado)
        error_msg = f"Error en el backup programado: {str(e)}"
        logger.error(error_msg)

def start_backup_scheduler():
    config = config_manager.load_config()["backup"]

    # Programación dinámica basada en el config_user.json
    for day in config["days"]:
        getattr(schedule.every(), day).at(config["time"]).do(job_backup)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Chequea cada minuto


def run_in_background():
    # Crea el hilo independiente
    t = threading.Thread(target=start_backup_scheduler, daemon=True)
    t.start()
    logger.info("🛡️ Backup Scheduler activado en segundo plano.")