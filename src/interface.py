import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import os
import time
import threading
import keyring
from config_controller import ConfigController
import gui_utils
import gui_dialogs
import gui_recovery
import gui_popup
import vigilance
import working_mode_ctrl

# 1. Configuración del ID único de la aplicación en Windows
gui_utils.set_app_id("gandalf_key")

# 2. Inicialización oculta inmediata (elimina cualquier parpadeo al arrancar)
window = tk.Tk()
window.withdraw()

window.title("Gandalf Security Panel 🛡️")
window.geometry("750x500")
window.resizable(False, False)

# Vincula el menú contextual universal para cajas de texto
gui_utils.deploy_context_menu(window)

# Icono universal de la ventana principal
try:
    icon_path = gui_utils.get_resource_path(os.path.join("img", "g_logo_3.ico"))
    window.iconbitmap(icon_path)
except Exception:
    pass

# 3. Lienzo y renderizado del degradado Gandalf
canvas = tk.Canvas(window, width=750, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)
background_img_pil = gui_utils.gandalf_gradient(750, 500)
background_img = ImageTk.PhotoImage(background_img_pil)
canvas.create_image(0, 0, anchor="nw", image=background_img)

canvas.create_text(375, 90, text="CENTINELA GANDALF", font=('Yu Gothic UI', 22, 'bold'), fill="#400835")

# LÓGICA DE OCULTAR/MOSTRAR
def hide_window():
    window.withdraw()

def show_window():
    # Llama al icono de la bandeja
    window.deiconify()
    window.attributes("-topmost", True)
    window.attributes("-topmost", False)

def open_settings(section_id):
    def on_verified():
        window.withdraw()
        has_key = keyring.get_password("Gandalf_Guard", "MASTER_KEY")
        config_app = ConfigController(is_setup_wizard=not has_key, initial_section=section_id)
        window.wait_window(config_app)
        window.deiconify()

    gui_dialogs.MasterKeyPrompt(window, on_success_callback=on_verified)

def desploy_settings_menu(origin_btn):
    # Crea y despliega el menú contextual justo debajo del engranaje
    contextual_menu = tk.Menu(window, tearoff=0)

    # Añade las opciones mapeadas a los IDs de los archivos modulares
    contextual_menu.add_command(label="📊 Configurar Backups y Logs", command=lambda: open_settings(3))
    contextual_menu.add_command(label="🔑 Claves de APIs y Cloud", command=lambda: open_settings(2))
    contextual_menu.add_separator()
    contextual_menu.add_command(label="🛡️ Cambiar Master Key", command=lambda: open_settings(1))

    # Calcula la posición del botón en la pantalla para que el menú flote justo debajo
    x = origin_btn.winfo_rootx()
    y = origin_btn.winfo_rooty() + origin_btn.winfo_height()
    contextual_menu.post(x, y)

def Comic_Dropdown_Call(btn):
    desploy_settings_menu(btn)

def action_recover_single():
    # Rescatar un solo archivo
    gui_recovery.action_recover_single(window, result_text_id, canvas)

def action_recover_all():
    # Recuperar el índice completo
    gui_recovery.action_recover_all(window, result_text_id, canvas)

def deploy_recovery_menu(origin_btn):
    # Crea y despliega el menú flotante para el botón de restauración
    recovery_menu = tk.Menu(window, tearoff=0)
    recovery_menu.add_command(label="📄 Restaurar un Archivo Específico", command=action_recover_single)
    recovery_menu.add_command(label="🚨 Restaurar Todo el Búnker", command=action_recover_all)

    x = origin_btn.winfo_rootx()
    y = origin_btn.winfo_rooty() + origin_btn.winfo_height()
    recovery_menu.post(x, y)

# LÓGICA DE CHECKING MANUAL (Placeholder y Funciones)
def on_entry_click(event):
    if url_entry.get() == 'Introduce URL sospechosa...':
        url_entry.delete(0, tk.END)
        url_entry.config(fg='#2c3e50')

def on_focusout(event):
    if url_entry.get() == '':
        url_entry.insert(0, 'Introduce URL sospechosa...')
        url_entry.config(fg='#95a5a6')

def manual_analysis():
    url = url_entry.get()
    if not url or url == 'Introduce URL sospechosa...':
        warn = gui_popup.DarkNotificationPopup(
            master=window,
            title="Atención",
            heading="Campo Requerido",
            description="Debes pegar la URL que quieres analizar.",
            button_text="Entendido"
        )
        warn.show()
        return

    run_analysis(url, modo="Manual")
    url_entry.delete(0, tk.END)
    window.focus()

def run_analysis(url, modo="Auto"):
    result, report = vigilance.analyze_url(url)
    color = "#1e6e06"  # Verde
    prefix = "✓ SEGURO"

    if result == "BLOQUEAR":
        color = "#b90113"  # Rojo
        prefix = "💀 PELIGRO"
    elif result == "DESCONOCIDO":
        color = "#8e3a00"  # Naranja
        prefix = "⚠️ AVISO"

    menssage = f"{modo}-Scan: {prefix}\n{report}"
    # Actualización segura en el hilo de Tkinter
    window.after(
        0, lambda: canvas.itemconfig(result_text_id, text=menssage, fill=color)
    )

# VIGILANCIA EN SEGUNDO PLANO
def background_monitor():
    last_url = ""
    while True:
        detected_url = vigilance.get_browser_url()
        if detected_url and detected_url != last_url:
            last_url = detected_url
            # Lanza el análisis en un hilo secundario
            threading.Thread(
                target=run_analysis,
                args=(detected_url,),
                kwargs={"modo": "Auto"},
                daemon=True,
            ).start()
        time.sleep(3)

# CONFIGURACIÓN DE LA VENTANA
# Entrada de URL
url_entry = tk.Entry(window, width=40, font=('Verdana', 11), borderwidth=0,
                       highlightthickness=1, highlightbackground="#bdc3c7", fg='#95a5a6')
url_entry.insert(0, 'Introduce URL sospechosa...')
url_entry.bind('<FocusIn>', on_entry_click)
url_entry.bind('<FocusOut>', on_focusout)
canvas.create_window(325, 150, window=url_entry, height=35)

# Botón
button_analize = tk.Button(window, text="Analizar Ahora", command=manual_analysis, bg="#231053", fg="white", font=('Verdana', 10, 'bold'),
padx=15, borderwidth=2, cursor="hand2")
canvas.create_window(375, 220, window=button_analize)

# Resultado
result_text_id = canvas.create_text(375, 270, text="Esperando URL...", font=("Verdana", 10, 'bold'), width=450, fill="#400835")

# Botón modo trabajo
btn_work_mode = tk.Button(
    window,
    text="🚫 WORK",
    bg="#b90113",
    fg="white",
font=('Verdana', 10, 'bold'),
    padx=20,
    pady=5,
    borderwidth=1,
    relief="flat",
    cursor="hand2"
)
btn_work_mode.config(command=lambda: working_mode_ctrl.toggle_work_mode(btn_work_mode))
canvas.create_window(375, 470, window=btn_work_mode)

# Botón config (Esquina Superior Derecha)
btn_gear = tk.Button(
    window,
    text="Config ⚙",
    font=("Arial", 9, 'bold'),
    bd=0,
    bg="#34495e",
    fg="#ecf0f1",
    activebackground="#2c3e50",
    activeforeground="#deff9a",
    cursor="hand2",
    relief="flat",
    padx=6,
    pady=2
)
btn_gear.config(command=lambda: Comic_Dropdown_Call(btn_gear))
canvas.create_window(695, 25, window=btn_gear)

# 🔄 BOTÓN RESTAURAR (Esquina Superior Izquierda)
btn_recover = tk.Button(
    window,
    text="Restaurar archivo 🔄",
    font=("Arial", 9, 'bold'),
    bd=0,
    bg="#27ae60",  # Un verde esmeralda elegante que denota vida/recuperación
    fg="white",
    activebackground="#1e8449",
    activeforeground="#deff9a",
    cursor="hand2",
    relief="flat",
    padx=6,
    pady=2
)
btn_recover.config(command=lambda: deploy_recovery_menu(btn_recover))
canvas.create_window(85, 25, window=btn_recover)

window.protocol("WM_DELETE_WINDOW", hide_window)
monitor_thread = threading.Thread(target=background_monitor, daemon=True)
monitor_thread.start()