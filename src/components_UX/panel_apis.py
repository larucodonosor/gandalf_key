import os
import tkinter as tk
import keyring
import webbrowser
from PIL import ImageTk
from components_UX.action_buttons import ActionButtons
import gui_utils
import gui_popup

class PanelAPIs(tk.Frame):
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
        # 3. Credenciales iniciales por si se cancela
        self._original_credentials = {
            "vt_api_key": keyring.get_password("Gandalf_Guard", "VT_API_KEY") or "",
            "telegram_token": keyring.get_password("Gandalf_Guard", "TELEGRAM_TOKEN") or "",
            "chat_id": keyring.get_password("Gandalf_Guard", "CHAT_ID") or "",
            "google_client_id": keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_ID") or "",
            "google_client_secret": keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_SECRET") or ""
        }
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
            text="🌐 GESTIÓN DE CREDENCIALES Y APIS",
            font=('Yu Gothic UI', 13, 'bold'),
            fill="#400835"
        )

        # Coordenada vertical base para distribuir individualmente los elementos
        y_pos = 100

        def render_section(label_text, default_value, show_char='🫧', link_text=None, link_url=None):
            nonlocal y_pos

            # Etiqueta de la credencial
            self.canvas.create_text(
                90, y_pos,
                anchor="w",
                text=label_text,
                font=('Arial', 9, 'bold'),
                fill="#2c3e50"
            )
            y_pos += 30

            # Sub-frame horizontal exclusivo para la caja de texto y su botón de visibilidad
            row_frame = tk.Frame(self.canvas, bg="", bd=0)
            entry = tk.Entry(
                row_frame,
                show=show_char,
                width=32,
                font=('Arial', 9),
                highlightthickness=1,
                highlightbackground="#bdc3c7"
            )
            entry.insert(0, default_value)
            entry.pack(side="left", ipady=2)

            btn_toggle = tk.Button(
                row_frame,
                text='Mostrar 🪄',
                font=('Arial', 8),
                bd=1,
                cursor="hand2",
                padx=4
            )
            btn_toggle.config(command=lambda e=entry, b=btn_toggle: self.toggle_visibility(e, b))
            btn_toggle.pack(side="left", padx=(6, 0))

            # Proyección del renglón interactivo sobre el lienzo
            self.canvas.create_window(250, y_pos, window=row_frame)
            y_pos += 27

            # Enlace de ayuda directo sobre el Canvas
            if link_text and link_url:
                link_id = self.canvas.create_text(
                    100, y_pos,
                    anchor="w",
                    text=link_text,
                    font=('Arial', 8, 'underline'),
                    fill="#0000ee"
                )
                self.canvas.tag_bind(link_id, "<Button-1>", lambda e: webbrowser.open_new(link_url))
                self.canvas.tag_bind(link_id, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(link_id, "<Leave>", lambda e: self.canvas.config(cursor=""))
                y_pos += 30
            else:
                y_pos += 20
            return entry

        # SECCIÓN VIRUSTOTAL
        self.entry_vt = render_section(
            label_text="API_KEY de Virus Total:",
            default_value=keyring.get_password("Gandalf_Guard", "VT_API_KEY") or "",
            link_text="¿Cómo obtener mi API Key?",
            link_url="https://www.virustotal.com/gui/my-apikey"
        )

        # SECCIÓN TELEGRAM
        self.entry_tel = render_section(
            label_text="Token de Telegram:",
            default_value=keyring.get_password("Gandalf_Guard", "TELEGRAM_TOKEN") or "",
            link_text="¿Cómo obtener mi Token?",
            link_url="https://core.telegram.org/bots/api"
        )

        self.entry_ci = render_section(
            label_text="Chat ID de Telegram:",
            default_value=keyring.get_password("Gandalf_Guard", "CHAT_ID") or "",
            link_text="¿Cómo obtener mi Chat ID?",
            link_url="https://t.me/userinfobot"
        )

        # SECCIÓN GOOGLE OAUTH
        self.entry_oauth_id = render_section(
            label_text="Google OAuth Client ID:",
            default_value=keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_ID") or "",
            link_text=None,
            link_url=None
        )

        self.entry_oauth_secret = render_section(
            label_text="Google OAuth Client Secret:",
            default_value=keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_SECRET") or "",
            link_text="¿Cómo obtener mis credenciales de Google?",
            link_url="https://console.cloud.google.com/apis/credentials"
        )

        # Botones
        self.actions = ActionButtons(
            canvas=self.canvas,
            center_x=250,
            center_y=y_pos + 25,
            on_save=self.save_changes,
            on_cancel=self.cancel_changes
        )

    def get_data(self):
        return {
            "vt_api_key": self.entry_vt.get(),
            "telegram_token": self.entry_tel.get(),
            "chat_id": self.entry_ci.get(),
            "google_client_id": self.entry_oauth_id.get(),
            "google_client_secret": self.entry_oauth_secret.get()
        }

    def cancel_changes(self):
        # 1. Restaura cada entrada al valor guardado en memoria
        self.entry_vt.delete(0, tk.END)
        self.entry_vt.insert(0, self._original_credentials["vt_api_key"])

        self.entry_tel.delete(0, tk.END)
        self.entry_tel.insert(0, self._original_credentials["telegram_token"])

        self.entry_ci.delete(0, tk.END)
        self.entry_ci.insert(0, self._original_credentials["chat_id"])

        self.entry_oauth_id.delete(0, tk.END)
        self.entry_oauth_id.insert(0, self._original_credentials["google_client_id"])

        self.entry_oauth_secret.delete(0, tk.END)
        self.entry_oauth_secret.insert(0, self._original_credentials["google_client_secret"])

    def save_changes(self):
        data = self.get_data()

        # Persistencia en keyring
        keyring.set_password("Gandalf_Guard", "VT_API_KEY", data["vt_api_key"])
        keyring.set_password("Gandalf_Guard", "TELEGRAM_TOKEN", data["telegram_token"])
        keyring.set_password("Gandalf_Guard", "CHAT_ID", data["chat_id"])
        keyring.set_password("Gandalf_Guard", "GOOGLE_CLIENT_ID", data["google_client_id"])
        keyring.set_password("Gandalf_Guard", "GOOGLE_CLIENT_SECRET", data["google_client_secret"])

        # Actualiza el estado de respaldo
        self._original_credentials = dict(data)
        return True
