import os
import sys
import tkinter as tk
from PIL import Image, ImageTk


class DarkNotificationPopup:
    def __init__(self, master, title, heading, description, button_text, callback_action, icon_name="g_logo_3", secondary_button_text=None, secondary_callback=None, is_alert=False):
        # self.root = tk.Tk()
        # self.root.withdraw()  # Oculta la raíz para controlar solo el Toplevel

        self.popup = tk.Toplevel()
        self.popup.title(title)
        self.popup.geometry("630x450")
        self.popup.configure(bg="#0f172a")
        self.popup.resizable(False, False)
        self.popup.transient(master)
        self.popup.grab_set()

        # Evita el cierre accidental si se requiere acción imperativa
        if callback_action or secondary_callback:
            self.popup.protocol("WM_DELETE_WINDOW", lambda: None)

        self.callback = callback_action
        self.secondary_callback = secondary_callback

        # Carga el icono
        def _get_resource_path(relative_path):
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(base_path, relative_path)

        # Carga el icono en el marco
        try:
            if getattr(sys, 'frozen', False):
                self.icon_path = _get_resource_path(f"{icon_name}.ico")
            else:
                self.icon_path = _get_resource_path(os.path.join("img", f"{icon_name}.ico"))

                # Doble verificación en desarrollo por si 'img' está fuera de 'src':
                if not os.path.exists(self.icon_path):
                    root_project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    self.icon_path = os.path.join(root_project, "src", "img", f"{icon_name}.ico")

            self.popup.iconbitmap(self.icon_path)
        except:
            self.icon_path = None

        # Contenedor
        frame = tk.Frame(self.popup, bg="#0f172a")
        frame.pack(expand=True, fill="both", padx=30, pady=15)

        # Imagen Dinámica
        uploaded_img = False
        try:
            if getattr(sys, 'frozen', False):
                png_path = _get_resource_path(f"{icon_name}.png")
            else:
                root_project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                png_path = os.path.join(root_project, "src", "img", f"{icon_name}.png")

            if os.path.exists(png_path):
                img = Image.open(png_path).convert("RGBA")
                img = img.resize((70, 70), Image.Resampling.LANCZOS)
                self.img_tk = ImageTk.PhotoImage(img)

                lbl_logo = tk.Label(frame, image=self.img_tk, bg="#0f172a")
                lbl_logo.pack(pady=10)
                uploaded_img = True

        except:
            if not uploaded_img:
                tk.Label(frame, text="✨ GANDALF GUARD ✨", font=("Segoe UI", 10, "bold"), bg="#0f172a",
                         fg="#a3e635").pack(pady=10)

        # Elementos de Texto Variables
        tk.Label(frame, text=heading, font=("Segoe UI", 16, "bold"), bg="#0f172a", fg="#deff9a").pack(pady=5)
        tk.Label(frame, text=description, font=("Segoe UI", 10), bg="#0f172a", fg="#cbd5e1", justify="center").pack(
            pady=10)

        btn_frame = tk.Frame(frame, bg="#0f172a")
        btn_frame.pack(side="bottom", fill="x", pady=20)

        # Color principal dinámico (Rojo carmesí si es alerta, Verde lima si es éxito/normal)
        main_btn_bg = "#870515" if is_alert else "#deff9a"
        main_btn_fg = "white" if is_alert else "#0f172a"
        main_btn_active = "#dc2626" if is_alert else "#a3e635"

        self.btn_main = tk.Button(
            btn_frame, text=button_text, font=("Segoe UI", 10, "bold"),
            bg=main_btn_bg, fg=main_btn_fg, activebackground=main_btn_active, activeforeground=main_btn_fg,
            bd=0, cursor="hand2", padx=20, pady=8, command=self._on_submit
        )

        # Si se requiere se pintan DOS botones uno al lado del otro
        if secondary_button_text:
            self.btn_main.pack(side="left", padx=15)

            tk.Button(
                btn_frame, text=secondary_button_text, font=("Segoe UI", 10, "bold"),
                bg="#334155", fg="#cbd5e1", activebackground="#475569", activeforeground="white",
                bd=0, cursor="hand2", padx=20, pady=8, command=self._on_secondary_submit
            ).pack(side="left", padx=15)
        else:
            # Si no hay botón secundario, el principal se queda en el centro como siempre
            self.btn_main.pack(anchor="center")

    def _on_submit(self):
        if self.callback:
            self.callback()
        self.popup.destroy()


    def _on_secondary_submit(self):
        if self.secondary_callback:
            self.secondary_callback()
        self.popup.destroy()

    def show(self):
        pass