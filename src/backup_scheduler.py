import json
import time
import threading
import schedule  # Si no lo tienes: pip install schedule
import backup_manager
from datetime import datetime

CONFIG_PATH = "config_user.json"
ESTADO_PATH = "estado_base.json"

def cargar_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)["backup"]

def job_backup():
    config = cargar_config()
    if not config["enabled"]:
        return
    print(f"[{datetime.now()}] Backup finalizado.")
    try:
        with open(ESTADO_PATH, "r") as f:
            estado_actual = json.load(f)

        # backup_manager ya tiene la lógica de subida,
        # Toma la lista de archivos que existen
        archivos = list(estado_actual.keys())
        backup_manager.run_scheduled_backup(archivos)
        print(f"[{datetime.now()}] Backup finalizado.")
    except Exception as e:
        print(f"Error en el backup programado: {e}")

def start_backup_scheduler():
    config = cargar_config()

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