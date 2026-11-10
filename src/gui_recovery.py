import os
import json
import tkinter as tk
from PIL import ImageTk

import gui_utils
import gui_popup
import recovery_manager
import index_manager


def action_recover_single(parent_window, result_text_id, canvas):
    # Maneja el flujo completo de selección y restauración de un archivo individual.
    index_path = index_manager.get_index_file_path()
    if not os.path.exists(index_path):
        popup = gui_popup.DarkNotificationPopup(
            master=parent_window,
            title="Error",
            heading="Índice no encontrado",
            description="No hay ningún índice de archivos creado todavía.",
            button_text="OK",
            is_alert=True
        )
        popup.show()
        return

    try:
        with open(index_path, 'r') as f:
            index = json.load(f)
    except Exception:
        index = {}

    if not index:
        popup = gui_popup.DarkNotificationPopup(
            master=parent_window,
            title="Sala de Resurrección",
            heading="Búnker Vacío",
            description="El búnker está vacío. No hay archivos protegidos que revivir.",
            button_text="Entendido"
        )
        popup.show()
        return

    # Ventana modal de selección con gandalf_gradient
    list_window = tk.Toplevel(parent_window)
    list_window.title("Selecciona el Tesoro a Restaurar 🪄")
    list_window.geometry("520x360")
    list_window.resizable(False, False)
    list_window.grab_set()

    try:
        icon_path = gui_utils.get_resource_path(os.path.join("img", "g_logo_3.ico"))
        list_window.iconbitmap(icon_path)
    except Exception:
        pass

    modal_canvas = tk.Canvas(list_window, width=520, height=360, highlightthickness=0)
    modal_canvas.pack(fill="both", expand=True)
    bg_pil = gui_utils.gandalf_gradient(520, 360)
    bg_tk = ImageTk.PhotoImage(bg_pil)
    modal_canvas.create_image(0, 0, anchor="nw", image=bg_tk)
    list_window._bg_cache = bg_tk

    modal_canvas.create_text(
        260, 30,
        text="Selecciona el archivo que deseas restaurar de la nube:",
        font=("Arial", 10, "bold"),
        fill="#400835"
    )

    frame = tk.Frame(list_window, bg="white", bd=1, relief="solid")
    scrollbar = tk.Scrollbar(frame, orient="vertical")
    file_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Consolas", 9), width=55, height=11)
    scrollbar.config(command=file_listbox.yview)

    scrollbar.pack(side="right", fill="y")
    file_listbox.pack(side="left", fill="both", expand=True)

    for real_path in index.keys():
        file_listbox.insert(tk.END, real_path)

    modal_canvas.create_window(260, 175, window=frame)

    def confirm_selection():
        selection = file_listbox.curselection()
        if not selection:
            alert = gui_popup.DarkNotificationPopup(
                master=list_window,
                title="Atención",
                heading="Archivo no seleccionado",
                description="Por favor, selecciona un archivo de la lista.",
                button_text="Entendido"
            )
            alert.show()
            return

        target_path = file_listbox.get(selection[0])
        list_window.destroy()

        canvas.itemconfig(result_text_id, text=f"Conectando con Drive para recuperar:\n{target_path}...", fill="#8e3a00")
        parent_window.update()
        try:
            success = recovery_manager.restore_single_file(target_path)
            if success:
                success_popup = gui_popup.DarkNotificationPopup(
                    master=parent_window,
                    title="Éxito 🪄",
                    heading="Archivo Restaurado",
                    description=f"El archivo ha sido restaurado:\n{target_path}",
                    button_text="Excelente"
                )
                success_popup.show()
                canvas.itemconfig(result_text_id, text="✓ Archivo restaurado con éxito.", fill="#1e6e06")
        except Exception as e:
            err_popup = gui_popup.DarkNotificationPopup(
                master=parent_window,
                title="Error de Recuperación",
                heading="Fallo al Restaurar",
                description=f"No se pudo recuperar el archivo:\n{e}",
                button_text="Cerrar",
                is_alert=True
            )
            err_popup.show()
            canvas.itemconfig(result_text_id, text="❌ Fallo en la resurrección individual.", fill="#b90113")

    btn_confirm = tk.Button(
        list_window,
        text="Restaurar Archivo Seleccionado 🪄",
        command=confirm_selection,
        bg="#27ae60",
        fg="white",
        font=("Arial", 10, "bold"),
        pady=5,
        padx=15,
        bd=0,
        cursor="hand2"
    )
    modal_canvas.create_window(260, 325, window=btn_confirm)


def action_recover_all(parent_window, result_text_id, canvas):
    # Maneja el flujo de confirmación y restauración masiva del búnker completo.
    def execute_all():
        canvas.itemconfig(result_text_id, text="Restaurando el búnker completo en segundo plano...", fill="#8e3a00")
        parent_window.update()
        try:
            total_recovered = recovery_manager.restore_full_backup()
            res_popup = gui_popup.DarkNotificationPopup(
                master=parent_window,
                title="Búnker Restaurado",
                heading="¡Proceso Completado!",
                description=f"Se han recuperado {total_recovered} archivos con éxito.",
                button_text="Finalizar"
            )
            res_popup.show()
            canvas.itemconfig(result_text_id, text=f"✓ Restauración completa exitosa ({total_recovered} archivos).", fill="#1e6e06")
        except Exception as e:
            err_popup = gui_popup.DarkNotificationPopup(
                master=parent_window,
                title="Error Crítico",
                heading="Fallo General",
                description=f"Fallo general en la restauración:\n{e}",
                button_text="Cerrar",
                is_alert=True
            )
            err_popup.show()
            canvas.itemconfig(result_text_id, text="❌ Fallo en la resurrección masiva.", fill="#b90113")

    confirm_popup = gui_popup.DarkNotificationPopup(
        master=parent_window,
        title="ALERTA MÁXIMA",
        heading="¿Iniciar una restauración completa?",
        description="Los archivos se recuperarán desde el último backup.\nPuede que pierda información no sincronizada en el proceso.",
        button_text="Sí, Restaurar Todo",
        callback_action=execute_all,
        secondary_button_text="Cancelar",
        secondary_callback=None,
        is_alert=True
    )
    confirm_popup.show()