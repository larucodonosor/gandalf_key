import tkinter as tk
import keyring


class PanelMasterKey(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.build_ui()

    def toggle_visibility(self, entry_field, button_widget):
        if entry_field.cget('show') == '':
            entry_field.config(show='🫧')
            button_widget.config(text='Mostrar 🪄')
        else:
            entry_field.config(show='')
            button_widget.config(text='Ocultar 🙈')

    def build_ui(self):
        tk.Label(self, text="🛡️ SEGURIDAD: CAMBIAR MASTER KEY", font=('Arial', 12, 'bold')).pack(pady=10)

        frame_pssw = tk.Frame(self)
        frame_pssw.pack(pady=5)

        tk.Label(frame_pssw, text='Nueva Contraseña Maestra:').grid(row=0, column=0, pady=5)
        self.entry_mk = tk.Entry(frame_pssw, show='🫧', width=30)
        saved_mk = keyring.get_password("Gandalf_Guard", "MASTER_KEY") or ""
        self.entry_mk.insert(0, saved_mk)
        self.entry_mk.grid(row=1, column = 0)

        btn_eye = tk.Button(frame_pssw, text='Mostrar 🪄')
        btn_eye.config(command=lambda: self.toggle_visibility(self.entry_mk, btn_eye))
        btn_eye.grid(row=1, column = 1, padx = 5)

        tk.Label(frame_pssw, text='Confirmación de Contraseña:').grid(row=2, column=0, pady=5)
        self.entry_ck = tk.Entry(frame_pssw, show='🫧', width=30)
        saved_ck = keyring.get_password("Gandalf_Guard", "Confirm_KEY") or ""
        self.entry_ck.insert(0, saved_ck)
        self.entry_ck.grid(row=3, column = 0)

        btn_check = tk.Button(frame_pssw, text='Mostrar 🪄')
        btn_check.config(command=lambda: self.toggle_visibility(self.entry_ck, btn_check))
        btn_check.grid(row=3, column = 1, padx = 5)

    def get_data(self):
        return {
            "master_key": self.entry_mk.get(),
            "confirm_key": self.entry_ck.get()
        }