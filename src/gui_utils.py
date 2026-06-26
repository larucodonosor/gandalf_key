import tkinter as tk


def deploy_context_menu(window):

    def deploy_menu(event):
        widget_under_mouse = window.winfo_containing(event.x_root, event.y_root)

        # Verifica que sea una caja de texto válida (Entry)
        if isinstance(widget_under_mouse, tk.Entry):
            # Fuerza el foco en ella para asegurar la acción
            widget_under_mouse.focus_set()
            # Crea el menú dinámico usando el widget padre que disparó el evento
            mouse_menu = tk.Menu(window, tearoff=0)

            mouse_menu.add_command(label="Cortar", command=lambda: widget_under_mouse.event_generate('<<Cut>>'))
            mouse_menu.add_command(label="Copiar", command=lambda: widget_under_mouse.event_generate('<<Copy>>'))
            mouse_menu.add_command(label="Pegar", command=lambda: widget_under_mouse.event_generate('<<Paste>>'))

            # Lo despliega exactamente donde el usuario hizo clic con el ratón
            mouse_menu.tk_popup(event.x_root, event.y_root)

    # Vincula el evento del Botón 3 del ratón (Clic derecho en Windows)
    window.bind_all('<Button-3>', deploy_menu)