import os
import tkinter as tk
from PIL import ImageTk
import keyring
from gui_utils import get_resource_path, gandalf_gradient
import gui_popup


class MasterKeyPrompt:
    # Ventana modal de autenticación con gandalf_gradient, burbujas 🫧 y varita 🪄.
    def __init__(self, master, on_success_callback):
        self.master = master
        self.on_success = on_success_callback
        self.is_password_visible = False

        self.prompt = tk.Toplevel(master)
        self.prompt.title("Verificación de Seguridad")
        self.prompt.geometry("380x210")
        self.prompt.resizable(False, False)
        self.prompt.grab_set()

        try:
            icon_path = get_resource_path(os.path.join("img", "g_logo_3.ico"))
            self.prompt.iconbitmap(icon_path)
        except Exception:
            pass

        self.canvas = tk.Canvas(self.prompt, width=380, height=210, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_pil = gandalf_gradient(380, 210)
        self.bg_tk = ImageTk.PhotoImage(self.bg_pil)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_tk)

        self.canvas.create_text(
            190, 40,
            text="Introduce la Master Key de Gandalf:",
            font=("Arial", 11, "bold"),
            fill="#400835"
        )

        box_frame = tk.Frame(self.prompt, bg="white", bd=1, relief="solid")
        self.entry_verify = tk.Entry(
            box_frame,
            show="🫧",
            width=20,
            font=("Arial", 11),
            bd=0,
            highlightthickness=0
        )
        self.entry_verify.pack(side="left", padx=6, pady=4)
        self.entry_verify.focus_set()
        self.entry_verify.bind("<Return>", lambda e: self.check_key())
        self.entry_verify.bind("<Control-v>", lambda e: self.entry_verify.event_generate("<<Paste>>"))

        self.btn_magic = tk.Button(
            box_frame,
            text="🪄",
            font=("Arial", 11),
            bd=0,
            bg="white",
            activebackground="white",
            cursor="hand2",
            command=self.toggle_key_visibility
        )
        self.btn_magic.pack(side="right", padx=4)

        self.canvas.create_window(190, 95, window=box_frame)

        btn_action = tk.Button(
            self.prompt,
            text="Verificar 🛡️",
            command=self.check_key,
            bg="#231053",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=4,
            cursor="hand2",
            bd=0
        )
        self.canvas.create_window(190, 160, window=btn_action)

    def toggle_key_visibility(self):
        if self.is_password_visible:
            self.entry_verify.config(show="🫧")
            self.is_password_visible = False
        else:
            self.entry_verify.config(show="")
            self.is_password_visible = True

    def check_key(self):
        master_key_real = keyring.get_password("Gandalf_Guard", "MASTER_KEY")
        if self.entry_verify.get() == master_key_real:
            self.prompt.destroy()
            self.on_success()
        else:
            self.prompt.destroy()
            alert = gui_popup.DarkNotificationPopup(
                master=self.master,
                title="Acceso Denegado",
                heading="¡Acceso Denegado!",
                description="Contraseña incorrecta. Intruso detectado.",
                button_text="Cerrar",
                is_alert=True
            )
            alert.show()