import json
import time
import threading
import schedule
import backup_manager
import logger_manager
import config_manager
from datetime import datetime

CONFIG_PATH = "config_user.json"
ESTADO_PATH = "estado_base.json"

def job_backup():
    # Configura el logger
    logger_manager.setup_logger()

    config = config_manager.cargar_config()["backup"]
    if not config["enabled"]:
        return

    # Limpieza de logs antiguos ANTES de hacer nada
    retention_days = config["retention_days", 30] # 30 es valor por defecto
    logger_manager.clean_old_logs(retention_days)

    # Log de inicio del proceso
    logger_manager.log_info("Iniciando backup programado...")

    try:
        with open(ESTADO_PATH, "r") as f:
            estado_actual = json.load(f)

        # Toma la lista de archivos que existen y llama a backup_manager que tiene la lógica de subida
        archivos = list(estado_actual.keys())
        backup_manager.run_scheduled_backup(archivos)
        # Log de éxito
        logger_manager.log_info(f"Backup finalizado con éxito: {len(archivos)} archivos procesados.")
    except Exception as e:
        # Log de error (si algo falla, queda registrado)
        error_msg = f"Error en el backup programado: {str(e)}"
        logger_manager.log_error(error_msg)

def start_backup_scheduler():
    config = config_manager.cargar_config()["backup"]

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
    print("🛡️ Backup Scheduler activado en segundo plano.")