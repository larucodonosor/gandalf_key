import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import alerts  # Tu módulo de Telegram


class DescargaHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            extension = os.path.splitext(file_path)[1].lower()

            # Solo vigila archivos potencialmente peligrosos
            if extension in ['.exe', '.msi', '.zip', '.rar', '.bat']:
                print(f"🕵️ Gandalf detectó nueva descarga: {os.path.basename(file_path)}")
                self.procesar_archivo(file_path)

    def procesar_archivo(self, ruta):
        # 1. Avisa del análisis
        alerts.registrar_log(f"Analizando descarga: {ruta}")

        # 2. Llama a VirusTotal
        # Si es sospechoso de tener componentes maliciosos
        print(f"🛡️ Bloqueando acceso a {ruta} hasta verificación...")

        # 3. MOVER A PRE-CUARENTENA (Para que no sea abierto)
        nombre = os.path.basename(ruta)
        ruta_espera = os.path.join("quarantine", f"WAITING_{nombre}")
        os.makedirs("quarantine", exist_ok=True)

        try:
            import shutil
            shutil.move(ruta, ruta_espera)

            # 4. LANZA PREGUNTA A TELEGRAM
            alerts.solicitar_autorizacion_remota(nombre, ruta_espera)

        except Exception as e:
            print(f"Error al mover archivo: {e}")


def iniciar_vigilancia_descargas():
    # Detecta la carpeta de descargas del usuario automáticamente
    ruta_descargas = os.path.join(os.path.expanduser('~'), 'Downloads')

    event_handler = DescargaHandler()
    observer = Observer()
    observer.schedule(event_handler, ruta_descargas, recursive=False)
    observer.start()
    print(f"🦅 Vigilante de descargas activado en: {ruta_descargas}")
    return observer