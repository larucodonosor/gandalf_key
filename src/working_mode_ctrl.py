import os
import sys
import threading
import keyring
from tkinter import simpledialog
import tkinter as tk
from typing import Optional
import logging

logger = logging.getLogger(__name__)

WORK_MODE_ACTIVE = False
button_reference: Optional[tk.Button] = None

import alerts

def toggle_work_mode(button):
    global WORK_MODE_ACTIVE, button_reference
    button_reference = button

    if not WORK_MODE_ACTIVE:
        logger.info("Solicitud de activación de Work Mode iniciada.")
        #  Pedir MASTER_KEY
        password = simpledialog.askstring("Security Check", "Enter MASTER_KEY to enable Work Mode:", show='*')
        master_key = keyring.get_password('Gandalf_guard', "MASTER_KEY")

        if not master_key:
            logger.error("Error de interfaz: No se encontró una Master Key registrada en el llavero seguro.")
            return

        if password == master_key:
            logger.info("MASTER_KEY validada localmente. Esperando verificación remota de dos factores...")
            # El envío se lanza en un hilo aparte para que no bloquee la UI de Tkinter
            threading.Thread(target=alerts.request_work_mode_verification, daemon=True).start()
            # El botón pasa a estado de espera controlado
            button.config(text="⏳ WAITING TELEGRAM...", bg="orange")
        else:
            logger.warning("Intento fallido de activación de Work Mode: Contraseña incorrecta introducida.")

    else:
        logger.info("Desactivando Work Mode manualmente.")
        update_work_mode_status(False)
        alerts.light_the_beacons("Work Mode Disabled. Guard Active.", severity="INFO")

def update_work_mode_status(status):
    # Esta función se llama desde alerts.py
    global WORK_MODE_ACTIVE
    WORK_MODE_ACTIVE = status
    logger.info(f"Estado de Work Mode actualizado a: {'ACTIVO' if status else 'INACTIVO'}")
    if button_reference is not None:
        button_reference.after(0, lambda: apply_visual_change(status))

def apply_visual_change(status):
    if button_reference is not None:
        if status:
            button_reference.config(text="WORK MODE: ON", bg="green")
        else:
            button_reference.config(text="🚫 WORK", bg="red")

