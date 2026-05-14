import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import alerts
import logging

logger = logging.getLogger(__name__)

class DescargaHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            extension = os.path.splitext(file_path)[1].lower()

            # Solo vigila archivos potencialmente peligrosos
            watched_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp',
                # ejecutables y Scripts
                '.exe', '.msi', '.bat', '.sh', '.ps1',
                # Comprimidos
                '.zip', '.rar', '.7z', '.tar.gz',
                # Multimedia
                '.mp4', '.mkv', '.avi', '.mov',  # Video
                '.mp3', '.wav', '.flac', '.aac',  # Audio
                '.jpg', '.jpeg', '.png', '.gif', '.svg'  # Imagen
                ]
            if extension in watched_extensions:
                logger.info(f" Gandalf detectó nueva descarga: {os.path.basename(file_path)}")
                self.process_file(file_path)

    def process_file(self, path):
        # 1. ESPERA ACTIVA: Asegura que el archivo terminó de descargarse
        # Si el tamaño cambia, es que sigue descargándose.
        prev_size = -1
        while prev_size != os.path.getsize(path):
            prev_size = os.path.getsize(path)
            time.sleep(1)  # Esperamos un segundo para volver a comprobar
        if not os.path.exists(path):
            return

        # 2. Avisa del análisis
        alerts.log_activity(f"Analizando descarga: {path}")

        # 3. Llama a VirusTotal
        # Si es sospechoso de tener componentes maliciosos
        logger.critical(f"🛡️ Bloqueando acceso a {path} hasta verificación...")

        # 4. MOVER A PRE-CUARENTENA (Para que no sea abierto)
        file_name = os.path.basename(path)
        quarantine_dir = "quarantine"
        waiting_path = os.path.join(quarantine_dir, f"WAITING_{file_name}")
        os.makedirs(quarantine_dir, exist_ok=True)

        try:
            shutil.move(path, waiting_path)
            logger.info(f"Archivo movido a pre-cuarentena: {waiting_path}")
            # 5. LANZA PREGUNTA A TELEGRAM
            alerts.request_remote_authorization(file_name, waiting_path)

        except Exception as e:
            logger.error(f"Error al mover archivo: {e}")


def start_downloads_guard():
    # Detecta la carpeta de descargas del usuario automáticamente
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    event_handler = DescargaHandler()
    observer = Observer()
    observer.schedule(event_handler, downloads_path, recursive=False)
    observer.start()
    print(f"🦅 Vigilante de descargas activado en: {downloads_path}")
    return observer