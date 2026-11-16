import threading
import tkinter as tk
from typing import Optional
import config_manager
import logging
import gui_dialogs

logger = logging.getLogger(__name__)

WORK_MODE_ACTIVE = False
button_reference: Optional[tk.Button] = None

import alerts

def toggle_work_mode(button):
    global WORK_MODE_ACTIVE, button_reference
    button_reference = button

    if not WORK_MODE_ACTIVE:
        logger.info("Solicitud de activación de Work Mode iniciada.")

        def on_key_verified():
            logger.info("MASTER_KEY validada localmente. Esperando verificación remota de dos factores...")
            # El envío se lanza en un hilo aparte para no bloquear la interfaz gráfica
            threading.Thread(target=alerts.request_work_mode_verification, daemon=True).start()
            # El botón pasa a estado de espera controlado
            button.config(text="⏳ WAITING TELEGRAM...", bg="orange")

        # Obtiene la ventana principal dueña del botón
        parent_window = button.winfo_toplevel()

        # Lanza el modal con degradado, burbujas y varita mágica
        gui_dialogs.MasterKeyPrompt(parent_window, on_success_callback=on_key_verified)

    else:
        logger.info("Desactivando Work Mode manualmente.")
        update_work_mode_status(False)
        alerts.light_the_beacons("Work Mode Disabled. Guard Active.", severity="INFO")

def update_work_mode_status(status):
    # Esta función se llama desde alerts.py
    global WORK_MODE_ACTIVE
    WORK_MODE_ACTIVE = status
    logger.info(f"Estado de Work Mode actualizado a: {'ACTIVO' if status else 'INACTIVO'}")

    try:
        # 1. Carga la configuración actual del usuario
        current_config = config_manager.load_config()

        # 2. Si no existe la sección "security", la crea
        if "security" not in current_config:
            current_config["security"] = {}

        # 3. Inyecta el nuevo estado del interruptor
        current_config["security"]["work_mode"] = status

        # 4. Fuerza al config_manager a sobreescribir el config_user.json
        config_manager.keep_config(current_config)
        logger.info("El estado de 'work_mode' se ha guardado con éxito en config_user.json.")

    except Exception as e:
        logger.error(f"Error crítico al guardar el estado: {e}")

    if button_reference is not None:
        button_reference.after(0, lambda: apply_visual_change(status))

def apply_visual_change(status):
    if button_reference is not None:
        if status:
            button_reference.config(text="WORK MODE: ON", bg="green")
        else:
            button_reference.config(text="🚫 WORK", bg="red")

