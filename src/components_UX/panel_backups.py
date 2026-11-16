import tkinter as tk
from tkinter import ttk
import config_manager
from PIL import ImageTk
import gui_utils
from components_UX.action_buttons import ActionButtons
import gui_popup


class PanelBackups(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Lienzo para el fondo degradado
        self.canvas = tk.Canvas(self, width=500, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Genera y ancla el degradado de Gandalf
        self.bg_pil = gui_utils.gandalf_gradient(500, 700)
        self.bg_tk = ImageTk.PhotoImage(self.bg_pil, master=self)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_tk)
        self._bg_cache = self.bg_tk  # Previene recolección de basura

        # Carga la config actual
        try:
            loaded_cfg = config_manager.load_config().get("backup", {})
        except Exception:
            loaded_cfg = {}

        self.current_config = {
            "days": list(loaded_cfg.get("days", [])),
            "time": loaded_cfg.get("time", "00:00"),
            "retention_days": int(loaded_cfg.get("retention_days", 30))
        }

        # Copia de seguridad en memoria para la función de cancelación
        self._original_config = {
            "days": list(self.current_config["days"]),
            "time": self.current_config["time"],
            "retention_days": self.current_config["retention_days"]
        }

        # Referencias a los elementos gráficos de las marcas de verificación ✔
        self.check_vars = {}
        self._check_marks = {}

        self.build_ui()

    def toggle_day(self, day, check_id):
        # Alterna el estado 0/1 y actualiza el símbolo ✔ en el Canvas
        new_val = 0 if self.check_vars[day].get() == 1 else 1
        self.check_vars[day].set(new_val)
        check_id = self._check_marks.get(day)
        if check_id:
            self.canvas.itemconfig(check_id, text="✔" if new_val == 1 else "")

    def build_ui(self):
        self.canvas.create_text(
            250, 50,
            text="📊 CONFIGURACIÓN DE BACKUPS Y LOGS",
            font=('Yu Gothic UI', 13, 'bold'),
            fill="#400835"
        )

        # DÍAS DE BACKUP
        self.canvas.create_text(
            80, 130,
            anchor="w",
            text="Días de Backup:",
            font=('Arial', 10, 'bold'),
            fill="#2c3e50"
        )

        week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        y_day = 165

        for day in week_days:
            # Estado activo/inactivo (1 o 0)
            is_checked = 1 if day in self.current_config.get("days", []) else 0
            self.check_vars[day] = tk.IntVar(self, value=is_checked)
            # 1. Recuadro exterior de la casilla
            box_id = self.canvas.create_rectangle(
                80, y_day - 8,
                96, y_day + 8,
                outline="#34495e",
                width=1.5,
                fill="#ffffff"
            )

            # 2. Marca de verificación ✔ en el centro del recuadro
            check_id = self.canvas.create_text(
                88, y_day,
                text="✔" if is_checked else "",
                font=('Arial', 10, 'bold'),
                fill="#0056b3"
            )
            self._check_marks[day] = check_id

            # Crea el texto independiente
            lbl_id = self.canvas.create_text(
                105, y_day,
                anchor="w",
                text=day.capitalize(),
                font=('Arial', 9, 'bold'),
                fill="#2c3e50"
            )
            # Vinculación de clic al cuadro, a la marca y a la etiqueta de texto
            handler = lambda e, d=day, c=check_id: self.toggle_day(d, c)
            for item in (box_id, check_id, lbl_id):
                self.canvas.tag_bind(item, "<Button-1>", handler)
                self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.config(cursor=""))

            y_day += 28

        # SECCIÓN HORA
        self.canvas.create_text(
            280, 130,
            anchor="w",
            text="Hora (HH:MM):",
            font=('Arial', 10, 'bold'),
            fill="#2c3e50"
        )

        self.entry_hour = tk.Entry(
            self.canvas,
            width=10,
            font=('Arial', 9),
            highlightthickness=1,
            highlightbackground="#bdc3c7"
        )
        self.entry_hour.insert(0, self.current_config.get("time", "00:00"))
        self.canvas.create_window(280, 165, anchor="w", window=self.entry_hour)

        # SECCIÓN TIEMPO DE RETENCIÓN
        self.canvas.create_text(
            280, 220,
            anchor="w",
            text="Días de retención de logs:",
            font=('Arial', 10, 'bold'),
            fill="#2c3e50"
        )

        retention_options = [15, 30, 45]
        self.dropdown = ttk.Combobox(
            self.canvas,
            values=retention_options,
            state="readonly",
            width=10
        )
        self.dropdown.set(self.current_config.get("retention_days", 30))
        self.canvas.create_window(280, 255, anchor="w", window=self.dropdown)

        # Botones submit/cancel
        self.actions = ActionButtons(
            canvas=self.canvas,
            center_x=250,
            center_y=410,
            on_save=self.save_changes,
            on_cancel=self.cancel_changes
        )

    def get_data(self):
        # Función "Getter" para cuando el Router decida guardar los cambios globales
        selected_days = [day for day, var in self.check_vars.items() if var.get() == 1]
        return {
            "days": selected_days,
            "time": self.entry_hour.get(),
            "retention_days": int(self.dropdown.get())
        }

    def cancel_changes(self):
        # 1. Restaura los días y sus marcas ✔
        saved_days = self._original_config["days"]
        for day, var in self.check_vars.items():
            active = 1 if day in saved_days else 0
            var.set(active)
            check_id = self._check_marks.get(day)
            if check_id:
                self.canvas.itemconfig(check_id, text="✔" if active else "")

        # 2. Restaura la hora
        self.entry_hour.delete(0, tk.END)
        self.entry_hour.insert(0, self._original_config["time"])

        # 3. Restaura el selector de retención
        self.dropdown.set(self._original_config["retention_days"])

    def save_changes(self):
        data = self.get_data()

        # Validación básica de formato de hora (HH:MM)
        time_val = data["time"]
        if len(time_val) != 5 or time_val[2] != ':':
            gui_popup.DarkNotificationPopup(
                master=self.winfo_toplevel(),
                title="Gandalf Guard",
                heading="Formato de hora incorrecto",
                description="La hora debe tener el formato exacto HH:MM (ejemplo: 03:00).",
                button_text="Corregir",
                is_alert=True
            ).show()
            return False


        # Actualiza y persiste mediante config_manager
        full_config = config_manager.load_config()
        full_config["backup"] = data
        config_manager.keep_config(full_config)

        # Actualiza el estado de referencia
        self._original_config = {
            "days": list(data["days"]),
            "time": data["time"],
            "retention_days": data["retention_days"]
        }
        return True

