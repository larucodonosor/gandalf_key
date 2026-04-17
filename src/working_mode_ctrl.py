import alerts
import os
import threading
from tkinter import simpledialog

WORK_MODE_ACTIVE = False
button_reference = None

def toggle_work_mode(button):
    global WORK_MODE_ACTIVE, button_reference
    button_reference = button

    if not WORK_MODE_ACTIVE:
        #  Pedir MASTER_KEY
        password = simpledialog.askstring("Security Check", "Enter MASTER_KEY to enable Work Mode:", show='*')
        if password == os.getenv("MASTER_KEY"):
            # El envío se lanza en un hilo aparte para que no bloquee otras funcionalidades
            threading.Thread(target=alerts.request_work_mode_verification, daemon=True).start()
            # El botón a espera
            button.config(text="⏳ WAITING TELEGRAM...", bg="orange")
        else:
            print("Clave incorrecta")
    else:
        update_work_mode_status(False)
        alerts.gritar_al_mundo("Work Mode Disabled. Guard Active.", nivel="INFO")

def update_work_mode_status(status):
    # Esta función se llama desde alerts.py
    global WORK_MODE_ACTIVE
    WORK_MODE_ACTIVE = status
    if button_reference is not None:
        button_reference.after(0, lambda: aplicar_cambio_visual(status))

def aplicar_cambio_visual(status):
    if button_reference is not None:
        if status:
            button_reference.config(text="WORK MODE: ON", bg="green")
        else:
            button_reference.config(text="🚫 WORK", bg="red")

