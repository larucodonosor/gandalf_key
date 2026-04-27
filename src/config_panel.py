import tkinter as tk
from tkinter import messagebox
import config_manager

def save_changes():
    selected_days = [day for day, var in check_vars.items() if var.get() == 1]
    hour = entry_hora.get()
    # Convierte los inputs en el dict que necesita
    config = {
        "backup": {
            "enabled": True,
            "days": selected_days, # Ejemplo: ["tuesday", "friday"]
            "time": hour  # Ejemplo: "03:00"
        }
    }
    config_manager.guardar_config(config)
    messagebox.showinfo("Gandalf", "Configuración actualizada correctamente.")
    root.destroy()

# Interfaz simple
root = tk.Tk()
root.title("Configuración de Gandalf")
root.geometry("300x350")

# Cargar config actual para mostrarla
current_config = config_manager.cargar_config()["backup"]

tk.Label(root, text="Días de Backup:").pack(pady=5)
check_vars = {}
week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

for day in week_days:
    var = tk.IntVar(value=1 if day in current_config["days"] else 0)
    check_vars[day] = var
    tk.Checkbutton(root, text=day.capitalize(), variable=var).pack(anchor="w")

tk.Label(root, text="Hora (HH:MM):").pack(pady=10)
entry_hora = tk.Entry(root)
entry_hora.insert(0, current_config["time"])
entry_hora.pack()

tk.Button(root, text="Guardar Cambios", command=save_changes).pack(pady=20)

root.mainloop()