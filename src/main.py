import time
import keyring
import threading
import tray_icon
import alerts
import backup_scheduler
import usb_manager
import logger_manager
import config_manager
from server_g_k import app as server_app
import updater
import wizard_cane
import logging

logger = logging.getLogger(__name__)

# Consulta la disponibilidad de actualizaciones al arrancar y luego cada 24 horas.
def infinite_updater_loop(root_window):
    while True:
        # Pasa la referencia de la ventana gráfica para que el Pop-up se ejecute en el hilo visual
        updater.check_for_updates_silently(root_window)
        # Duerme 24 horas (60s * 60m * 24h)
        time.sleep(86400)

def launch_gandalf_guard_threads(interface_window):

    # 1. Hilo de telegram (Polling) daemon=True para que se cierre si se cierra el programa principal
    token_telegram = keyring.get_password("Gandalf_Guard", "TELEGRAM_TOKEN")
    if token_telegram:
        threading.Thread(target=alerts.start_bot_polling, daemon=True).start()

    # 2. Hilo de vigilancia de descargas (Watchdog)
    import downloads_guard
    threading.Thread(target=downloads_guard.start_downloads_guard, daemon=True).start()

    # 3. Activa el servidor Flask
    threading.Thread(target=lambda: server_app.run(port=61103, use_reloader=False), daemon=True).start()

    # 4. Lanza el bucle de vigilancia en su Hilo (Daemon)
    threading.Thread(target=wizard_cane.infinite_surveillance_loop, daemon=True).start()

    # 5. Lanza los backups periodizados
    backup_scheduler.run_in_background()

    # 6. Inicia la bandeja
    threading.Thread(target=tray_icon.start_tray, daemon=True).start()

    # 7. Actualizador automatizado
    threading.Thread(target=infinite_updater_loop, args=(interface_window,), daemon=True).start()

if __name__ == "__main__":
    logger.info(f"🛡️ Gandalf v{updater.CURRENT_VERSION} iniciando guardia...")

    # Inicialización del Sistema de Logs
    try:
        user_config = config_manager.load_config()
        retention_days = user_config.get("backup", {}).get("retention_days", 7)
    except Exception:
        retention_days = 7
    logger_manager.setup_logger(days_to_keep=retention_days)

    # Verificación de la instalación y primera ejecución
    has_key = keyring.get_password("Gandalf_Guard", "MASTER_KEY")
    if not has_key:
        logger.info("Primera ejecución detectada. Lanzando Asistente de Configuración Independiente...")
        from config_controller import ConfigController

        wizard = ConfigController(is_setup_wizard=True)
        wizard.deiconify()
        wizard.lift()
        wizard.attributes("-topmost", True)
        wizard.attributes("-topmost", False)
        wizard.mainloop()
        logger.info("✅ Asistente completado con éxito. Inicializando motores principales...")

    # Asegura el autoarranque del sistema
    wizard_cane.ensure_persistence()

    # Carga diferida de la interfaz de usuario
    import interface

    # Activa el gestor de hardware pasivo sobre la ventana visual
    usb_manager.start_passive_surveillance(interface.window)

    # Lanza todos los hilos concurrentes de forma controlada
    launch_gandalf_guard_threads(interface.window)

    # Bucle principal de eventos de la GUI (Mantiene viva la aplicación)
    interface.window.mainloop()


