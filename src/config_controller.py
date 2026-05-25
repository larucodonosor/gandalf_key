import tkinter as tk
from tkinter import messagebox
import keyring
import config_manager
import gui_utils
from components_UX.panel_backups import PanelBackups
from components_UX.panel_apis import PanelAPIs
from components_UX.panel_master_key import PanelMasterKey


class ConfigController(tk.Tk):
    def __init__(self, is_setup_wizard=False):
        super().__init__()
        self.title("Gandalf Control Center")
        self.geometry("500x700")
        self.is_setup_wizard = is_setup_wizard

        # El contenedor
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        gui_utils.deploy_context_menu(self)

        if self.is_setup_wizard:
            self.show_wizard_step(1)
        else:
            self.show_main_menu()

    def show_wizard_step(self, step):
        # Limpia el frame actual
        for widget in self.container.winfo_children():
            widget.destroy()

        if step == 1:
            self.current_panel = PanelMasterKey(self.container)
            self.current_panel.pack(fill="both", expand=True)
            tk.Button(self.container, text="Siguiente: APIs ➔", command=lambda: self.validate_and_next(from_step=1, to_step=2)).pack(pady=20)

        elif step == 2:
            self.current_panel = PanelAPIs(self.container)
            self.current_panel.pack(fill="both", expand=True)
            tk.Button(self.container, text="Siguiente: Backups ➔", command=lambda: self.validate_and_next(from_step=2, to_step=3)).pack(
                pady=20)

        elif step == 3:
            self.current_panel = PanelBackups(self.container)
            self.current_panel.pack(fill="both", expand=True)
            tk.Button(self.container, text="Finalizar Instalación ✅", command=lambda: self.validate_and_next(from_step=3, to_step=None)).pack(pady=20)

    def validate_and_next(self, from_step, to_step):
        # Intercepta el avance para comprobar que los datos obligatorios existen
        if from_step == 1:
            # Extrae los datos que el usuario ha escrito en los inputs del panel activo
            data = self.current_panel.get_data()
            master_key = data.get("master_key", "").strip()
            confirm_key = data.get("confirm_key", "").strip()

            # Candado 1: Campo vacío
            if not master_key:
                messagebox.showwarning("🛡️ Gandalf Guard",
                                       "¡Atención! La Master Key es obligatoria para inicializar el cifrado.")
                return  # Congela la pantalla aquí

            # Candado 2: Contraseñas diferentes
            if master_key != confirm_key:
                messagebox.showerror("Error", "Las contraseñas no coinciden. Por favor, verifícalas.")
                return  # Congelar la pantalla aquí

            # Si pasa los dos candados con éxito, guarda de forma segura en el llavero
            keyring.set_password("Gandalf_Guard", "MASTER_KEY", master_key)
            keyring.set_password("Gandalf_Guard", "Confirm_KEY", confirm_key)

            self.show_wizard_step(to_step)

        elif from_step == 2:
            # 🚀 Captura los datos del PanelAPIs
            data = self.current_panel.get_data()

            # Guarda en el llavero con los nombres oficiales definitivos
            keyring.set_password("Gandalf_Guard", "VT_API_KEY", data.get("vt_api_key", "").strip())
            keyring.set_password("Gandalf_Guard", "TELEGRAM_TOKEN", data.get("telegram_token", "").strip())
            keyring.set_password("Gandalf_Guard", "CHAT_ID", data.get("chat_id", "").strip())
            keyring.set_password("Gandalf_Guard", "GOOGLE_CLIENT_ID", data.get("google_client_id", "").strip())
            keyring.set_password("Gandalf_Guard", "GOOGLE_CLIENT_SECRET", data.get("google_client_secret", "").strip())

            # Avanza a la pantalla de copias de seguridad (Paso 3)
            self.show_wizard_step(to_step)

        elif from_step == 3:
            backup_data = self.current_panel.get_data()
            config = {
                "backup": {
                    "enabled": True,
                    "days": backup_data.get("days", []),
                    "time": backup_data.get("time", "00:00"),
                    "retention_days": backup_data.get("retention_days", 30)
                }
            }
            config_manager.keep_config(config)
            self.finish_setup()

    def on_closing(self):
        # Filtro de seguridad para la 'X' de la ventana
        # Si esta en el asistente inicial y NO hay una clave guardada en el sistema...
        if self.is_setup_wizard and not keyring.get_password("Gandalf_Guard", "MASTER_KEY"):
            messagebox.showwarning("Cierre Bloqueado 🚫",
                                   "Debes configurar la Master Key obligatoriamente para inicializar las defensas de Gandalf antes de salir.",
                                   parent=self)
        else:
            # Si ya hay clave o no es el asistente de instalación, permite cerrar normalmente
            self.destroy()

    def show_main_menu(self):
        pass

    def finish_setup(self):
        # Lógica global de guardado
        messagebox.showinfo("Gandalf", "Instalación completada. Protegiendo tesoros...")
        self.destroy()


if __name__ == "__main__":
    # Lógica de detección: ¿Falta la Master Key? -> Wizard. ¿Existe? -> Menú.
    has_key = keyring.get_password("Gandalf_Guard", "MASTER_KEY")
    app = ConfigController(is_setup_wizard=not has_key)
    app.mainloop()

