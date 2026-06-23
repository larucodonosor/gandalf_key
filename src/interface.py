import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random
import os
import sys
import time
import threading
import keyring
from config_controller import ConfigController
import gui_utils
import vigilance
import working_mode_ctrl
import recovery_manager

# FUNCIÓN DE MANEJO DE LA RUTA PARA EL EJECUTABLE
def get_resource_path(relative_path):
    # Retorna la ruta absoluta para recursos (imágenes, iconos),
    # soportando tanto el entorno de desarrollo como el ejecutable .exe
    if getattr(sys, 'frozen', False):
        # Carpeta temporal donde PyInstaller desempaqueta los assets
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# LÓGICA DE OCULTAR/MOSTRAR
def hide_window():
    window.withdraw()

def show_window():
    # Llama al icono de la bandeja
    window.deiconify()
    window.attributes("-topmost", True)
    window.attributes("-topmost", False)


def open_settings(section_id):
    # Pide la contraseña maestra antes de permitir el acceso a cualquier sección del panel de configuración.
    # 1. Recupera la contraseña real guardada en el llavero seguro
    master_key_real = keyring.get_password("Gandalf_Guard", "MASTER_KEY")

    # 2. Crea una pequeña ventana pop-up temporal para pedir la clave
    prompt = tk.Toplevel()
    prompt.title("Verificación de Seguridad")
    prompt.geometry("300x150")
    prompt.resizable(False, False)
    prompt.grab_set()  # Bloquea la ventana principal hasta que responda

    tk.Label(prompt, text="Introduce la Master Key de Gandalf:", font=("Arial", 10, "bold")).pack(pady=15)
    entry_verify = tk.Entry(prompt, show="🫧", width=25)
    entry_verify.pack()
    entry_verify.focus_set()

    entry_verify.bind("<Control-v>", lambda e: entry_verify.event_generate("<<Paste>>"))

    def check_key():
        if entry_verify.get() == master_key_real:
            prompt.destroy()
            window.withdraw()
            # Caso éxito, lanza el controlador pasándole la sección exacta
            # Cierra la app de fondo si hace falta, o lo abre como Toplevel
            has_key = keyring.get_password("Gandalf_Guard", "MASTER_KEY")
            config_app = ConfigController(is_setup_wizard=not has_key, initial_section=section_id)
            window.wait_window(config_app)
            window.deiconify()
        else:
            messagebox.showerror("Acceso Denegado", "Contraseña incorrecta. Intruso detectado.")
            prompt.destroy()

    tk.Button(prompt, text="Verificar 🛡️", command=check_key).pack(pady=15)


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

def action_recover_single():
    # Lógica para rescatar un solo archivo
    import json
    import index_manager

    index_path = index_manager.get_index_file_path()
    if not os.path.exists(index_path):
        messagebox.showerror("Error", "No hay ningún índice de archivos creado todavía.")
        return

    with open(index_path, 'r') as f:
        index = json.load(f)

    if not index:
        messagebox.showinfo("Sala de Resurrección", "El búnker está vacío. No hay archivos protegidos que revivir.")
        return

        # Crea una ventana emergente para mostrar la lista de archivos protegidos
    list_window = tk.Toplevel(window)
    list_window.title("Selecciona el Tesoro a Retaurar 🪄")
    list_window.geometry("500x350")
    list_window.grab_set()

    tk.Label(list_window, text="Selecciona el archivo que deseas restaurar de la nube:",
             font=("Arial", 10, "bold")).pack(pady=10)

    # Lista los archivos con scrollbar
    frame = tk.Frame(list_window)
    frame.pack(fill="both", expand=True, padx=20, pady=5)

    scrollbar = tk.Scrollbar(frame, orient="vertical")
    file_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Consolas", 9))
    scrollbar.config(command=file_listbox.yview)

    scrollbar.pack(side="right", fill="y")
    file_listbox.pack(side="left", fill="both", expand=True)

    # Mete todas las rutas que Gandalf conoce dentro de la lista
    for real_path in index.keys():
        file_listbox.insert(tk.END, real_path)

    def confirm_selection():
        selection = file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Atención", "Por favor, selecciona un archivo de la lista.")
            return

        target_path = file_listbox.get(selection[0])
        list_window.destroy()  # Cierra la lista
        # Lanza la recuperación de la ruta seleccionada
        canvas.itemconfig(result_text_id, text=f"Conectando con Drive para recuperar:\n{target_path}...", fill="#8e3a00")
        window.update()
        try:
            success = recovery_manager.restore_single_file(target_path)
            if success:
                messagebox.showinfo("Éxito 🪄", f"El archivo ha sido restaurado:\n{target_path}")
                canvas.itemconfig(result_text_id, text=f"✓ Archivo restaurado con éxito.", fill="#1e6e06")
        except Exception as e:
            messagebox.showerror("Error de Recuperación", f"No se pudo recuperar el archivo:\n{e}")
            canvas.itemconfig(result_text_id, text="❌ Fallo en la resurrección individual.", fill="#b90113")
    tk.Button(list_window, text="Restaurar Archivo Seleccionado", command=confirm_selection, bg="#27ae60", fg="white", font=("Arial", 10, "bold"), pady=5).pack(pady=15)

def action_recover_all():
    # Lógica de para recuperar el índice completo
    confirm = messagebox.askyesno(
        "ALERTA MÁXIMA",
        "¿Iniciar una restauración completa?\n Los archivos se recuperaran desde el último backup.\n Puede que pierda información en el proceso."
    )
    if not confirm:
        return

    canvas.itemconfig(result_text_id, text="Restaurando el búnker completo en segundo plano...", fill="#8e3a00")
    window.update()
    try:
        total_recovered = recovery_manager.restore_full_backup()
        messagebox.showinfo("Búnker Restaurado",
                                f"¡Proceso completado!\nSe han recuperado {total_recovered} archivos con éxito.")
        canvas.itemconfig(result_text_id, text=f"✓ Restauración completa exitosa ({total_recovered} archivos).",
                              fill="#1e6e06")
    except Exception as e:
        messagebox.showerror("Error Crítico", f"Fallo general en la restauración: {e}")
        canvas.itemconfig(result_text_id, text="❌ Fallo en la resurrección masiva.", fill="#b90113")

def deploy_recovery_menu(origin_btn):
    # Crea y despliega el menú flotante para el botón de restauración
    recovery_menu = tk.Menu(window, tearoff=0)
    recovery_menu.add_command(label="📄 Restaurar un Archivo Específico", command=action_recover_single)
    recovery_menu.add_command(label="🚨 Restaurar Todo el Búnker", command=action_recover_all)

    x = origin_btn.winfo_rootx()
    y = origin_btn.winfo_rooty() + origin_btn.winfo_height()
    recovery_menu.post(x, y)

# LÓGICA DE DISEÑO
def gandalf_gradient(width, height):
    # Definición de los colores
    colors = [
        (178, 206, 247), (136, 247, 181), (253, 253, 37, 186),
        (255, 186, 21, 222), (245, 195, 195), (221, 182, 247)
    ]
    img = Image.new('RGB', (width, height), colors[0][:3])

    for color in colors[1:]:
        layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for _ in range(9):
            radio = random.randint(30, 140) # nosec
            x, y = random.randint(0, width), random.randint(0, height) # nosec
            rgb = color[:3]
            alpha_val = color[3] if len(color) > 3 else 30
            draw.ellipse([x - radio, y - radio, x + radio, y + radio], fill=(*rgb, alpha_val))
        layer = layer.filter(ImageFilter.GaussianBlur(40))
        img.paste(layer, (0, 0), layer)
    return img

# LÓGICA DE CONTROL (Placeholder y Funciones)
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
        messagebox.showerror("Atención", "Debes pegar la URL que quieres analizar.")
        return
    run_analysis(url, modo="Manual")
    # La url desaparece al terminar el proceso
    url_entry.delete(0, tk.END)
    # Devuelve el foco para que aparezca el placeholder
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
    canvas.itemconfig(result_text_id, text=menssage, fill=color)

# VIGILANCIA EN SEGUNDO PLANO
def background_monitor():
    last_url = ""
    while True:
        detected_url = vigilance.get_brownser_url()
        if detected_url and detected_url != last_url:
            last_url = detected_url
            # Actualiza la interfaz de forma segura
            window.after(0, lambda u=detected_url: run_analysis(u, modo="Auto"))
        time.sleep(3)

# CONFIGURACIÓN DE LA VENTANA
window = tk.Tk()
window.title("Gandalf Security Panel 🛡️")
window.geometry("750x500")

try:
    import ctypes
    myappid = 'lara.gandalf.key.1.0'  # ID único para tu app
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

gui_utils.deploy_context_menu(window)
# Icono
icon_path = get_resource_path(os.path.join("img", "g_logo_3.ico"))
try:
    window.iconbitmap(icon_path)
except:
    pass

canvas = tk.Canvas(window, width=750, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)
background_img_pil = gandalf_gradient(750, 500)
background_img = ImageTk.PhotoImage(background_img_pil)
canvas.create_image(0, 0, anchor="nw", image=background_img)

canvas.create_text(375, 90, text="CENTINELA GANDALF", font=('Yu Gothic UI', 22, 'bold'), fill="#400835")
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

# 7. Botón config (Esquina Superior Derecha)
btn_engranaje = tk.Button(
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
btn_engranaje.config(command=lambda: Comic_Dropdown_Call(btn_engranaje))
canvas.create_window(695, 25, window=btn_engranaje)

def Comic_Dropdown_Call(btn):
    # Envoltura rápida para coordinar con la función desplegar_menu_config
    desploy_settings_menu(btn)

# 8. 🔄 BOTÓN RESTAURAR (Esquina Superior Izquierda)
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
window.withdraw()
monitor_thread = threading.Thread(target=background_monitor, daemon=True)
monitor_thread.start()