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

logger = logging.getLogger(__name__)

# Estandariza las rutas  para que sean accesibles tanto en desarrollo como en producción.
def get_secure_path(filename):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.path.basename(current_dir) in ["src", "config", "components_UX"]:
            base_dir = os.path.dirname(current_dir)
        else:
            base_dir = current_dir
    return os.path.join(base_dir, filename)

ESTADO_PATH = get_secure_path("base_memory.json")

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
            logger.warning(f"No se encontró el archivo de estado {ESTADO_PATH}.")
            return

        with open(ESTADO_PATH, "r", encoding="utf-8") as f:
            estado_actual = json.load(f)

        # Toma la lista de archivos que existen y a backup_manager que tiene la lógica de subida
        files = list(estado_actual.keys())
        if not files:
            logger.warning("El registro de tesoros está vacío. Nada que sincronizar en la nube.")
            return
        logger.info(f"Pasando {len(files)} tesoros al gestor de subidas...")
        backup_manager.run_scheduled_backup(files)
        # Log de éxito
        logger.info(f"Backup finalizado con éxito: {len(files)} archivos procesados.")
    except Exception as e:
        error_msg = f"Error en el backup programado: {str(e)}"
        logger.error(error_msg)

def start_backup_scheduler():
    last_known_config = None
    while True:
        try:
            config = config_manager.load_config()["backup"]
            if config != last_known_config:
                schedule.clear()

                # Programación dinámica basada en el config_user.json
                for day in config["days"]:
                    getattr(schedule.every(), day).at(config["time"]).do(job_backup)
                logger.info( f"🔄 Agenda de Backups actualizada: Días: {config['days']} a las {config['time']}")
                last_known_config = config
            schedule.run_pending()
        except Exception as e:
            logger.error(f"Error en el bucle del planificador: {e}")

        time.sleep(60)  # Chequea cada minuto


def run_in_background():
    # Crea el hilo independiente
    t = threading.Thread(target=start_backup_scheduler, daemon=True)
    t.start()
    logger.info("🛡️ Backup Scheduler activado en segundo plano.")