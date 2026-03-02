import os
import shutil

def asegurar_boveda(rutas):
    """Revisa las carpetas y protege los archivos .py que no estén en la bóveda."""
    os.makedirs(".gandalf_vault", exist_ok=True)
    for r in rutas:
        if not os.path.exists(r): continue
        for f in os.listdir(r):
            ruta_completa = os.path.join(r, f)
            if os.path.isfile(ruta_completa) and f.endswith(".py"):
                ruta_destino = os.path.join(".gandalf_vault", f)
                if not os.path.exists(ruta_destino):
                    shutil.copy2(ruta_completa, ruta_destino)
                    print(f"📦 Copia de seguridad inicial: {f}")

def restaurar_archivo(ruta_afectada):
    ruta_vault = os.path.join(".gandalf_vault", os.path.basename(ruta_afectada))
    if os.path.exists(ruta_vault):
        print(f"🩹 Iniciando autocuración para: {ruta_afectada}")
        shutil.copy2(ruta_vault, ruta_afectada)
        print(f"✨ Archivo restaurado con éxito desde la bóveda.")
        return True
    else:
        print(f"⚠️ No hay copia de seguridad en la bóveda para {ruta_afectada}")
        return False