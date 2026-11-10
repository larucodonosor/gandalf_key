import tkinter as tk
import keyring
from PIL import ImageTk
from components_UX.action_buttons import ActionButtons
import gui_utils
import gui_popup


class PanelMasterKey(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # 1. Lienzo para el fondo degradado
        self.canvas = tk.Canvas(self, width=500, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 2. Genera y ancla el degradado de Gandalf
        self.bg_pil = gui_utils.gandalf_gradient(500, 700)
        self.bg_tk = ImageTk.PhotoImage(self.bg_pil, master=self)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_tk)
        self._bg_cache = self.bg_tk  # Previene recolección de basura por Python
        # Referencia a las credenciales iniciales si se cancela
        self._original_mk = keyring.get_password("Gandalf_Guard", "MASTER_KEY") or ""
        self._original_ck = keyring.get_password("Gandalf_Guard", "Confirm_KEY") or ""

        self.build_ui()

    def toggle_visibility(self, entry_field, button_widget):
        if entry_field.cget('show') == '':
            entry_field.config(show='🫧')
            button_widget.config(text='Mostrar 🪄')
        else:
            entry_field.config(show='')
            button_widget.config(text='Ocultar 🙈')

    def build_ui(self):
        self.canvas.create_text(
            250, 50,
            text="🔑 CAMBIAR MASTER KEY",
            font=('Yu Gothic UI', 13, 'bold'),
            fill="#400835"
        )

        # SECCIÓN CONTRASEÑA
        self.canvas.create_text(
            110, 140,
            anchor="w",
            text="Nueva Contraseña Maestra:",
            font=('Arial', 9, 'bold'),
            fill="#2c3e50"
        )

        row_mk = tk.Frame(self.canvas, bd=0)
        self.entry_mk = tk.Entry(
            row_mk,
            show='🫧',
            width=26,
            font=('Arial', 9),
            highlightthickness=1,
            highlightbackground="#bdc3c7"
        )
        saved_mk = keyring.get_password("Gandalf_Guard", "MASTER_KEY") or ""
        self.entry_mk.insert(0, saved_mk)
        self.entry_mk.grid(row=1, column = 0, ipady=2)

        btn_eye = tk.Button(row_mk, text='Mostrar 🪄', font=('Arial', 8), bd=1, cursor="hand2")
        btn_eye.config(command=lambda: self.toggle_visibility(self.entry_mk, btn_eye))
        btn_eye.grid(row=1, column = 1, padx = 5)

        self.canvas.create_window(250, 170, window=row_mk)

        # SECCIÓN CONFIRMACIÓN CONTRASEÑA

        self.canvas.create_text(
            110, 220,
            anchor="w",
            text="Confirmación de Contraseña:",
            font=('Arial', 9, 'bold'),
            fill="#2c3e50"
        )

        row_ck = tk.Frame(self.canvas, bd=0)
        self.entry_ck = tk.Entry(
            row_ck,
            show='🫧',
            width=26,
            font=('Arial', 9),
            highlightthickness=1,
            highlightbackground="#bdc3c7"
        )
        saved_ck = keyring.get_password("Gandalf_Guard", "Confirm_KEY") or ""
        self.entry_ck.insert(0, saved_ck)
        self.entry_ck.grid(row=3, column = 0, ipady=2)

        btn_check = tk.Button(row_ck, text='Mostrar 🪄', font=('Arial', 8), bd=1, cursor="hand2")
        btn_check.config(command=lambda: self.toggle_visibility(self.entry_ck, btn_check))
        btn_check.grid(row=3, column = 1, padx =(6, 0))

        self.canvas.create_window(250, 250, window=row_ck)

        # Botón 'submit'
        self.actions = ActionButtons(
            canvas=self.canvas,
            center_x=250,
            center_y=320,
            on_save=self.save_changes,
            on_cancel=self.cancel_changes
        )

    def get_data(self):
        return {
            "master_key": self.entry_mk.get(),
            "confirm_key": self.entry_ck.get()
        }

    def cancel_changes(self):
        # Restaura los campos de entrada al estado original
        self.entry_mk.delete(0, tk.END)
        self.entry_mk.insert(0, self._original_mk)

        self.entry_ck.delete(0, tk.END)
        self.entry_ck.insert(0, self._original_ck)

    def save_changes(self):
        # 1. Obtención de datos actuales del panel
        data = self.get_data()
        mk = data["master_key"]
        ck = data["confirm_key"]

        # Validación básica de coincidencia
        if not mk or not ck:
            gui_popup.DarkNotificationPopup(
                master=self.canvas.winfo_toplevel(),
                title="Gandalf Guard",
                heading="Campos incompletos",
                description="Ninguno de los campos de contraseña puede quedar vacío.",
                button_text="Corregir",
                is_alert=True
            ).show()
            return False
        if mk != ck:
            gui_popup.DarkNotificationPopup(
                master=self.canvas.winfo_toplevel(),
                title="Gandalf Guard",
                heading="Error de coincidencia",
                description="Las contraseñas introducidas no coinciden. Verifica que sean idénticas.",
                button_text="Corregir",
                is_alert=True
            ).show()
            return False

        keyring.set_password("Gandalf_Guard", "MASTER_KEY", mk)
        keyring.set_password("Gandalf_Guard", "Confirm_KEY", ck)

        # Actualiza el estado anterior si se cancela
        self._original_mk = mk
        self._original_ck = ck
        return True



