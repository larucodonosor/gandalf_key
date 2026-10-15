import sys
import subprocess

# --- 1. ADAPTADOR WINDOWS (Ruta exacta descubierta) ---
def _get_firefox_url_windows(window_obj):
    try:
        import ctypes
        import uiautomation as auto

        # 1. Asegurar que la accesibilidad Gecko esté despierta
        if window_obj and hasattr(window_obj, "NativeWindowHandle"):
            hwnd = window_obj.NativeWindowHandle
            if hwnd:
                user32 = ctypes.windll.user32
                WM_GETOBJECT = 0x003D
                OBJID_CLIENT = 0xFFFFFFFC
                user32.SendMessageW(hwnd, WM_GETOBJECT, 0, OBJID_CLIENT)

        if window_obj:
            # 2. Navegación directa por la jerarquía confirmada
            nav_bar = window_obj.ToolBarControl(AutomationId="nav-bar")
            if nav_bar.Exists(0.2, 0):
                urlbar = nav_bar.GroupControl(AutomationId="urlbar")
                if urlbar.Exists(0.2, 0):
                    # Localizamos el ComboBoxControl identificado en el diagnóstico
                    input_box = urlbar.ComboBoxControl(AutomationId="urlbar-input")
                    if not input_box.Exists(0.1, 0):
                        input_box = urlbar.EditControl(AutomationId="urlbar-input")

                    if input_box.Exists(0.1, 0):
                        val = None
                        try:
                            legacy = input_box.GetLegacyIAccessiblePattern()
                            if legacy and legacy.Value:
                                val = legacy.Value
                        except Exception:
                            pass

                        if not val:
                            try:
                                val = input_box.GetValuePattern().Value
                            except Exception:
                                pass

                        if val and ("." in val):
                            clean_val = val.strip()
                            return clean_val if clean_val.startswith("http") else f"https://{clean_val}"

            # 3. Fallback por título si la pestaña apenas está cargando
            raw_title = window_obj.Name or ""
            clean_title = raw_title.replace(" — Mozilla Firefox", "").replace(" - Mozilla Firefox", "").strip()
            if clean_title:
                for part in clean_title.split():
                    if "." in part and not part.endswith((".py", ".sh", ".txt", ".exe")):
                        return f"https://{part}" if not part.startswith("http") else part

    except Exception:
        pass
    return None


# --- 2. ADAPTADOR MACOS (AppleScript) ---
def _get_firefox_url_darwin():
    script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            if frontApp is "Firefox" then
                tell process "Firefox"
                    return name of front window
                end tell
            end if
        end tell
        return ""
    '''
    try:
        title = subprocess.check_output(["osascript", "-e", script], text=True).strip()
        clean_title = title.replace(" — Mozilla Firefox", "").replace(" - Mozilla Firefox", "").strip()
        for part in clean_title.split():
            if "." in part and not part.endswith((".py", ".sh", ".txt")):
                return f"https://{part}" if not part.startswith("http") else part
    except Exception:
        pass
    return None


# --- 3. ADAPTADOR LINUX (xdotool / X11) ---
def _get_firefox_url_linux():
    try:
        out = subprocess.check_output(
            ["xdotool", "getactivewindow", "getwindowname"],
            text=True
        ).strip()
        clean_out = out.replace(" — Mozilla Firefox", "").replace(" - Mozilla Firefox", "").strip()
        for part in clean_out.split():
            if "." in part and not part.endswith((".py", ".sh", ".txt")):
                return f"https://{part}" if not part.startswith("http") else part
    except Exception:
        pass
    return None


# --- 4. FUNCIÓN PÚBLICA PRINCIPAL ---
def get_firefox_url(window_obj=None):
    os_name = sys.platform
    if os_name.startswith("win"):
        return _get_firefox_url_windows(window_obj)
    elif os_name == "darwin":
        return _get_firefox_url_darwin()
    elif os_name.startswith("linux"):
        return _get_firefox_url_linux()
    return None