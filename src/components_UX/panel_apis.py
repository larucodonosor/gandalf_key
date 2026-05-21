import tkinter as tk
import keyring
import webbrowser


class PanelAPIs(tk.Frame):
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
        tk.Label(self, text="GESTIÓN DE CREDENCIALES Y APIS", font=('Arial', 12, 'bold')).pack(pady=10)

        frame_pssw = tk.Frame(self)
        frame_pssw.pack(pady=5)

        # --- SECCIÓN VIRUSTOTAL ---
        tk.Label(frame_pssw, text='API_KEY de Virus Total:').grid(row=0, column=0, pady=2)
        self.entry_vt = tk.Entry(frame_pssw, show='🫧', width=40)
        self.entry_vt.insert(0, keyring.get_password("Gandalf_Guard", "VT_API_KEY") or "")
        self.entry_vt.grid(row=1, column=0)

        link_vt = tk.Label(frame_pssw, text="¿Cómo obtener mi API Key?", fg="blue", cursor="hand2")
        link_vt.grid(row=2, column=0)
        link_vt.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.virustotal.com/gui/my-apikey"))

        btn_show = tk.Button(frame_pssw, text='Mostrar 🪄')
        btn_show.config(command=lambda: self.toggle_visibility(self.entry_vt, btn_show))
        btn_show.grid(row=1, column=1, padx=5)

        # --- SECCIÓN TELEGRAM ---
        tk.Label(frame_pssw, text='Token de Telegram:').grid(row=3, column=0, pady=2)
        self.entry_tel = tk.Entry(frame_pssw, show='🫧', width=40)
        self.entry_tel.insert(0, keyring.get_password("Gandalf_Guard", "TELEGRAM_TOKEN") or "")
        self.entry_tel.grid(row=4, column=0)

        link_tel = tk.Label(frame_pssw, text="¿Cómo obtener mi Token?", fg="blue", cursor="hand2")
        link_tel.grid(row=5, column=0)
        link_tel.bind("<Button-1>", lambda e: webbrowser.open_new("https://core.telegram.org/bots/api"))

        btn_tel = tk.Button(frame_pssw, text='Mostrar 🪄')
        btn_tel.config(command=lambda: self.toggle_visibility(self.entry_tel, btn_tel))
        btn_tel.grid(row=4, column=1, padx=5)

        tk.Label(frame_pssw, text='Chat ID de Telegram:').grid(row=6, column=0, pady=2)
        self.entry_ci = tk.Entry(frame_pssw, show='🫧', width=40)
        self.entry_ci.insert(0, keyring.get_password("Gandalf_Guard", "CHAT_ID") or "")
        self.entry_ci.grid(row=7, column=0)

        link_ci = tk.Label(frame_pssw, text="¿Cómo obtener mi Chat ID?", fg="blue", cursor="hand2")
        link_ci.grid(row=8, column=0)
        link_ci.bind("<Button-1>", lambda e: webbrowser.open_new("https://t.me/userinfobot"))

        btn_ci = tk.Button(frame_pssw, text='Mostrar 🪄')
        btn_ci.config(command=lambda: self.toggle_visibility(self.entry_ci, btn_ci))
        btn_ci.grid(row=7, column=1, padx=5)

        # --- ✨ NUEVA SECCIÓN: GOOGLE OAUTH CREDENTIALS ✨ ---
        tk.Label(frame_pssw, text='Google OAuth Client ID:', font=('Arial', 10, 'bold')).grid(row=9, column=0,
                                                                                              pady=(15, 2))
        self.entry_oauth_id = tk.Entry(frame_pssw, show='🫧', width=40)
        self.entry_oauth_id.insert(0, keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_ID") or "")
        self.entry_oauth_id.grid(row=10, column=0)

        btn_oauth_id = tk.Button(frame_pssw, text='Mostrar 🪄')
        btn_oauth_id.config(command=lambda: self.toggle_visibility(self.entry_oauth_id, btn_oauth_id))
        btn_oauth_id.grid(row=10, column=1, padx=5)
        link_oauth_id = tk.Label(frame_pssw, text="¿Cómo obtener mis credenciales de Google?", fg="blue", cursor="hand2")
        link_oauth_id.grid(row=11, column=0)
        link_oauth_id.bind("<Button-1>", lambda e: webbrowser.open_new("https://console.cloud.google.com/apis/credentials"))

        tk.Label(frame_pssw, text='Google OAuth Client Secret:', font=('Arial', 10, 'bold')).grid(row=12, column=0,                                                                                          pady=2)
        self.entry_oauth_secret = tk.Entry(frame_pssw, show='🫧', width=40)
        self.entry_oauth_secret.insert(0, keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_SECRET") or "")
        self.entry_oauth_secret.grid(row=13, column=0)

        btn_oauth_sec = tk.Button(frame_pssw, text='Mostrar 🪄')
        btn_oauth_sec.config(command=lambda: self.toggle_visibility(self.entry_oauth_secret, btn_oauth_sec))
        btn_oauth_sec.grid(row=13, column=1, padx=5)

    def get_data(self):
        return {
            "vt_api_key": self.entry_vt.get(),
            "telegram_token": self.entry_tel.get(),
            "chat_id": self.entry_ci.get(),
            "google_client_id": self.entry_oauth_id.get(),
            "google_client_secret": self.entry_oauth_secret.get()
        }
