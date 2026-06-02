import tkinter as tk
from tkinter import ttk
import config_manager


class PanelBackups(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Carga la config actual
        try:
            self.current_config = config_manager.load_config()["backup"]
        except Exception:
            self.current_config = {"days": [], "time": "00:00", "retention_days": 30}

        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="⚙️ CONFIGURACIÓN DE BACKUPS Y LOGS", font=('Arial', 12, 'bold')).pack(pady=10)

        frame_backup = tk.Frame(self)
        frame_backup.pack(pady=10)

        # Días de la semana
        frame_days = tk.Frame(frame_backup)
        frame_days.grid(row=0, column=0, padx=20)
        tk.Label(frame_days, text="Días de Backup:", font=('Arial', 10, 'bold')).pack()

        self.check_vars = {}
        week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        for day in week_days:
            var = tk.IntVar(self, value=1 if day in self.current_config["days"] else 0)
            self.check_vars[day] = var
            tk.Checkbutton(frame_days, text=day.capitalize(), variable=var).pack(anchor="w")

        # Hora
        frame_hour = tk.Frame(frame_backup)
        frame_hour.grid(row=0, column=1, sticky="n")
        tk.Label(frame_hour, text="Hora (HH:MM):", font=('Arial', 10, 'bold')).pack(pady=5)
        self.entry_hour = tk.Entry(frame_hour, width=10)
        self.entry_hour.insert(0, self.current_config["time"])
        self.entry_hour.pack()

        # Tiempo de retención
        tk.Label(self, text="Días de retención de logs:", font=('Arial', 10, 'bold')).pack(pady=5)
        retention_options = [15, 30, 45]
        self.dropdown = ttk.Combobox(self, values=retention_options, state="readonly", width=10)
        self.dropdown.set(self.current_config.get("retention_days", 30))
        self.dropdown.pack(pady=5)

    def get_data(self):
        # Función "Getter" para cuando el Router decida guardar los cambios globales
        selected_days = [day for day, var in self.check_vars.items() if var.get() == 1]
        return {
            "days": selected_days,
            "time": self.entry_hour.get(),
            "retention_days": int(self.dropdown.get())
        }