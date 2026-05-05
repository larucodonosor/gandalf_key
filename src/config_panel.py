import tkinter as tk
from tkinter import messagebox
import keyring
import webbrowser
import config_manager

def save_changes():
    # Compara la contraseña creada y su confirmación
    password = entry_mk.get()
    confirm = entry_ck.get()
    if password != confirm:
        messagebox.showerror("Las contraseñas no coinciden")
        return

    try:
        selected_days = [day for day, var in check_vars.items() if var.get() == 1]
        hour = entry_hora.get()
        # Captura la preferencia de tiempo de retención del user.
        retention = int(retention_var.get())

        config = {
            "backup": {
                "enabled": True,
                "days": selected_days,
                "time": hour,
                "retention_days": retention # Guarda el valor
            }
        }
        config_manager.guardar_config(config)

        # Guarda las claves fuera del JSON por seguridad
        keyring.set_password("Gandalf_Guard", "VT_API_KEY", entry_vt.get())
        keyring.set_password("Gandalf_Guard", "TELEGRAM_TOKEN", entry_tel.get())
        keyring.set_password("Gandalf_Guard", "CHAT_ID", entry_ci.get())
        keyring.set_password("Gandalf_Guard", "MASTER_KEY", entry_mk.get())
        keyring.set_password("Gandalf_Guard", "Confirm_KEY", entry_ck.get())

        messagebox.showinfo("Gandalf", "Configuración actualizada correctamente.")
        root.destroy()
    except ValueError:
        messagebox.showerror("Error", "Error al procesar la configuración.")

# Configura la interfaz
root = tk.Tk()
root.title("Configuración de Gandalf")
root.geometry("350x600")

# Carga la config actual
current_config = config_manager.cargar_config()["backup"]

# Días
tk.Label(root, text="Días de Backup:").pack(pady=5)
check_vars = {}
week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

for day in week_days:
    var = tk.IntVar(value=1 if day in current_config["days"] else 0)
    check_vars[day] = var
    tk.Checkbutton(root, text=day.capitalize(), variable=var).pack(anchor="w")

# Hora
tk.Label(root, text="Hora (HH:MM):").pack(pady=10)
entry_hora = tk.Entry(root)
entry_hora.insert(0, current_config["time"])
entry_hora.pack()

# Tiempo de retención
tk.Label(root, text="Días de retención de logs:").pack(pady=5)
retention_options = [15, 30, 45]
retention_var = tk.StringVar(root)
retention_var.set(str(current_config.get("retention_days", 30)))
dropdown = tk.OptionMenu(root, retention_var, *retention_options)
dropdown.pack()

# Claves de API y personales:
def open_help_vt(event):
    webbrowser.open_new("https://www.virustotal.com/gui/my-apikey")
tk.Label(root, text='API_KEY de Virus Total:').pack(pady=5)
entry_vt = tk.Entry(root)
entry_vt.insert(0, current_config.get("VT_API_KEY", ""))
entry_vt.pack()
# Crea el Label que parece un link
link_vt = tk.Label(root, text="¿Cómo obtener mi API Key de VirusTotal?", fg="blue", cursor="hand2")
link_vt.pack()
# Ata el clic del ratón (Button-1) a la función
link_vt.bind("<Button-1>", open_help_vt)

def open_help_tel(event):
    webbrowser.open_new("https://core.telegram.org/bots/api")
tk.Label(root, text='Token de Telegram:').pack(pady=5)
entry_tel = tk.Entry(root)
entry_tel.insert(0, current_config.get("TELEGRAM_TOKEN", ""))
entry_tel.pack()
# Crea el Label que parece un link
link_tel = tk.Label(root, text="¿Cómo obtener mi Token de Telegram?", fg="blue", cursor="hand2")
link_tel.pack()
# Ata el clic del ratón (Button-1) a la función
link_tel.bind("<Button-1>", open_help_tel)

def open_help_ci(event):
    webbrowser.open_new("https://t.me/userinfobot")
tk.Label(root, text='Chat ID de Telegram').pack(pady=5)
entry_ci = tk.Entry(root)
entry_ci.insert(0, current_config.get("CHAT_ID", ""))
entry_ci.pack()
# Crea el Label que parece un link
link_ci = tk.Label(root, text="¿Cómo obtener mi chat id de telegram?", fg="blue", cursor="hand2")
link_ci.pack()
# Ata el clic del ratón (Button-1) a la función
link_ci.bind("<Button-1>", open_help_ci)
tk.Label(root, text='Crea tu contraseña para operar con Gandalf').pack(pady=5)
entry_mk = tk.Entry(root)
entry_mk.insert(0, current_config.get("MASTER_KEY", ""))
entry_mk.pack()
tk.Label(root, text='Confirmación de contraseña').pack(pady=5)
entry_ck = tk.Entry(root)
entry_ck.pack()


# Botón de guardado
tk.Button(root, text="Guardar Cambios", command=save_changes).pack(pady=20)

root.mainloop()