import tkinter as tk
import gui_popup

class ActionButtons(tk.Frame):
    # Botos reutilizable con confirmaciones modales automáticas
    def __init__(self, canvas, center_x, center_y, on_save, on_cancel):
        self.canvas = canvas
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Botón Guardar
        self.btn_save = tk.Button(
            self.canvas,
            text="Guardar",
            font=('Yu Gothic UI', 9, 'bold'),
            bg="#400835",
            fg="#ffffff",
            activebackground="#5a0d4b",
            activeforeground="#ffffff",
            relief="raised",
            bd=2,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._handle_save
        )

        # Botón Cancelar con relieve
        self.btn_cancel = tk.Button(
            self.canvas,
            text="Cancelar",
            font=('Yu Gothic UI', 9, 'bold'),
            bg="#7f8c8d",
            fg="#ffffff",
            activebackground="#95a5a6",
            activeforeground="#ffffff",
            relief="raised",
            bd=2,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._handle_cancel
        )
        self.canvas.create_window(
            center_x - 65, center_y, window=self.btn_save, anchor="center"
        )
        self.canvas.create_window(
            center_x + 65, center_y, window=self.btn_cancel, anchor="center"
        )

    def _handle_save(self):
        try:
            # Ejecuta la función de guardado del panel. Si retorna False (error de validación), se detiene.
            success = self.on_save()

            if success is False:
                return
            # Referencia a la ventana principal contenedora
            top_window = self.canvas.winfo_toplevel()

            gui_popup.DarkNotificationPopup(
                master=top_window,
                title="Gandalf Guard",
                heading="Actualización correcta",
                description="Tus cambios se han actualizado correctamente.",
                button_text="Aceptar",
                callback_action=top_window.destroy,
                is_alert=False
            ).show()

        except Exception as e:
            parent_window = self.canvas.winfo_toplevel()
            gui_popup.DarkNotificationPopup(
                master=parent_window,
                title="Gandalf Guard",
                heading="Error al guardar",
                description=f"Ocurrió un error inesperado al aplicar los cambios:\n{e}",
                button_text="Entendido",
                is_alert=True
            ).show()


    def _handle_cancel(self):
        # Despliega confirmación previa antes de restaurar
        top_window = self.canvas.winfo_toplevel()
        gui_popup.DarkNotificationPopup(
            master=top_window,
            title="Gandalf Guard",
            heading="¿Descartar cambios?",
            description="¿Seguro que deseas descartar los cambios?",
            button_text="Sí, descartar",
            callback_action=self.on_cancel,
            secondary_button_text="Continuar editando",
            secondary_callback=None,
            is_alert=True
        ).show()