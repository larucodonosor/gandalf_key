import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import keyring
import webbrowser
import config_manager
import logging

logger = logging.getLogger(__name__)

def validate_fields():
    mandatory_fields = {
        "API Key de VirusTotal": entry_vt.get(),
        "Token de Telegram": entry_tel.get(),
        "Contraseña Maestra": entry_mk.get()
    }
    for name, value in mandatory_fields.items():
        if not value.strip():  # El .strip() evita engaño con espacios en blanco
            messagebox.showwarning("Campo incompleto", f"El campo '{name}' no puede estar vacío.")
            return  # Detenemos la ejecución aquí mismo

    if entry_mk.get() != entry_ck.get():
        messagebox.showerror("Error", "Las contraseñas no coinciden.")
        return False
    return True

def save_changes():
    if not validate_fields():
        return

    try:
        selected_days = [day for day, var in check_vars.items() if var.get() == 1]
        hour = entry_hour.get()
        # Captura la preferencia de tiempo de retención del user.
        retention = int(dropdown.get())

        config = {
            "backup": {
                "enabled": True,
                "days": selected_days,
                "time": hour,
                "retention_days": retention # Guarda el valor
            }
        }
        config_manager.keep_config(config)

        # Guarda las claves fuera del JSON por seguridad
        keyring.set_password("Gandalf_Guard", "VT_API_KEY", entry_vt.get())
        keyring.set_password("Gandalf_Guard", "TELEGRAM_TOKEN", entry_tel.get())
        keyring.set_password("Gandalf_Guard", "CHAT_ID", entry_ci.get())
        keyring.set_password("Gandalf_Guard", "MASTER_KEY", entry_mk.get())
        keyring.set_password("Gandalf_Guard", "Confirm_KEY", entry_ck.get())

        messagebox.showinfo("Gandalf", "Configuración actualizada correctamente.")
        root.destroy()
    except Exception as e:
        logger.error(f"Error crítico al guardar la configuración: {e}")
        messagebox.showerror("Error", "Error al procesar la configuración.")

def on_closing():
    if validate_fields():
        root.destroy()
    else:
        messagebox.showwarning("Cierre bloqueado", "Debes configurar correctamente las claves antes de salir.")

# Configura la interfaz
root = tk.Tk()
root.option_add("*Label.font", "Arial 10 bold")
root.title("Configuración de Gandalf")
root.geometry("430x800")

# Carga la config actual
try:
    current_config = config_manager.load_config()["backup"]
except Exception:
    # Fallback si el archivo no existe o está corrupto
    current_config = {"days": [], "time": "00:00", "retention_days": 30}

# Días
frame_backup = tk.Frame(root)
frame_backup.pack(pady=10)

frame_days = tk.Frame(frame_backup)
frame_days.grid(row=0, column=0, padx=20)
tk.Label(frame_days, text="Días de Backup:", font=('Arial', 10, 'bold')).pack()
check_vars = {}
week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

for day in week_days:
    var = tk.IntVar(value=1 if day in current_config["days"] else 0)
    check_vars[day] = var
    tk.Checkbutton(frame_days, text=day.capitalize(), variable=var).pack(anchor="w")

# Hora
frame_hour = tk.Frame(frame_backup)
frame_hour.grid(row=0, column=1, sticky="n")
tk.Label(frame_hour, text="Hora (HH:MM):", font=('Arial', 10, 'bold')).pack(pady=5)
entry_hour = tk.Entry(frame_hour, width=10)
entry_hour.insert(0, current_config["time"])
entry_hour.pack()

# Tiempo de retención
tk.Label(root, text="Días de retención de logs:").pack(pady=5)
retention_options = [15, 30, 45]
dropdown = ttk.Combobox(root, values=retention_options, state="readonly", width=10)
dropdown.set(current_config.get("retention_days", 30))
dropdown.pack(pady=5)

# Claves de API y personales:
def toggle_visibility(entry_field, button_widget):
    if entry_field.cget('show') == '':
        entry_field.config(show='🫧')
        button_widget.config(text='Mostrar 🪄')
    else:
        entry_field.config(show='')
        button_widget.config(text='Ocultar 🙈')

frame_pssw = tk.Frame(root)
frame_pssw.pack(pady=5)
def open_help_vt(event):
    webbrowser.open_new("https://www.virustotal.com/gui/my-apikey")
tk.Label(frame_pssw, text='API_KEY de Virus Total:').grid(row=0, column=0, pady=5)
entry_vt = tk.Entry(frame_pssw, show='🫧', width=50)
entry_vt.insert(0, current_config.get("VT_API_KEY", ""))
entry_vt.grid(row=1, column=0)
# Crea el Label que parece un link
link_vt = tk.Label(frame_pssw, text="¿Cómo obtener mi API Key de VirusTotal?", fg="blue", cursor="hand2")
link_vt.grid(row=2, column=0)
# Ata el clic del ratón (Button-1) a la función; (Button -1) == click izquierdo.
link_vt.bind("<Button-1>", open_help_vt)
btn_show = tk.Button(frame_pssw, text='Mostrar 🪄', command=lambda: toggle_visibility(entry_vt, btn_show))
btn_show.grid(row=1, column=1, pady=5, padx=5)

def open_help_tel(event):
    webbrowser.open_new("https://core.telegram.org/bots/api")
tk.Label(frame_pssw, text='Token de Telegram:').grid(row=3, column=0, pady=5)
entry_tel = tk.Entry(frame_pssw, show='🫧', width=50)
entry_tel.insert(0, current_config.get("TELEGRAM_TOKEN", ""))
entry_tel.grid(row=4, column=0)
# Label/link
link_tel = tk.Label(frame_pssw, text="¿Cómo obtener mi Token de Telegram?", fg="blue", cursor="hand2")
link_tel.grid(row=5, column=0)
# Ata el clic
link_tel.bind("<Button-1>", open_help_tel)
btn_open = tk.Button(frame_pssw, text='Mostrar 🪄', command=lambda: toggle_visibility(entry_tel, btn_open))
btn_open.grid(row=4, column=1 ,pady=5, padx=5)

def open_help_ci(event):
    webbrowser.open_new("https://t.me/userinfobot")
tk.Label(frame_pssw, text='Chat ID de Telegram').grid(row=6, column=0, pady=5)
entry_ci = tk.Entry(frame_pssw, show='🫧', width=50)
entry_ci.insert(0, current_config.get("CHAT_ID", ""))
entry_ci.grid(row=7, column=0)
# Crea el Label/link
link_ci = tk.Label(frame_pssw, text="¿Cómo obtener mi chat id de telegram?", fg="blue", cursor="hand2")
link_ci.grid(row=8, column=0)
# Ata el clic del ratón (Button-1) a la función
link_ci.bind("<Button-1>", open_help_ci)
btn_tgl = tk.Button(frame_pssw, text='Mostrar 🪄', command=lambda: toggle_visibility(entry_ci, btn_tgl))
btn_tgl.grid(row=7, column=1 ,pady=5, padx=5)

tk.Label(frame_pssw, text='Crea tu contraseña para operar con Gandalf').grid(row=9, column=0, pady=5)
entry_mk = tk.Entry(frame_pssw, show='🫧', width=30)
entry_mk.insert(0, current_config.get("MASTER_KEY", ""))
entry_mk.grid(row=10, column=0)
btn_eye = tk.Button(frame_pssw, text='Mostrar 🪄', command=lambda: toggle_visibility(entry_mk, btn_eye))
btn_eye.grid(row=10, column=1,pady=5, padx=5)

tk.Label(frame_pssw, text='Confirmación de contraseña').grid(row=11, column=0, pady=5)
entry_ck = tk.Entry(frame_pssw, show='🫧', width=30)
entry_ck.grid(row=12, column=0)
btn_check = tk.Button(frame_pssw, text='Mostrar 🪄', command=lambda: toggle_visibility(entry_ck, btn_check))
btn_check.grid(row=12, column=1, pady=5, padx=5)

# Intercepta la X de la ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Botón de guardado
tk.Button(root, text="Guardar Cambios", command=save_changes).pack(pady=20)


root.mainloop()