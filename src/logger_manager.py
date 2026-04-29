import logging
import os
import time
from datetime import datetime

# Configuración básica
LOG_FILE = "gandalf.log"

def setup_logger():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )

def log_info(mensaje):
    logging.info(mensaje)

def log_error(mensaje):
    logging.error(mensaje)

# Limpia logs antiguos (retención elegida por el usuario)
def clean_old_logs(days_to_keep):
    if os.path.exists(LOG_FILE):
        file_time = os.path.getmtime(LOG_FILE)
        if (time.time() - file_time) > (days_to_keep * 86400):
            os.remove(LOG_FILE)
            print("Logs antiguos eliminados por política de retención.")