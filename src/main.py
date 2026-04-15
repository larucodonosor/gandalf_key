import json
import os
import shutil
import time
import sys
import threading
import tray_icon
import alertas
import seguridad
import interfaz
from scanner import mapear_carpeta, validar_adn
from servidor_g_k import app as servidor_app

TIEMPO_ESPERA = 30

def ejecutar_gandalf():
    ruta = ["./", "./src"]
    archivo_memoria = "estado_base.json"
    EXTENSIONES_IGNORAR = [".log", ".tmp", ".json"]
    ARCHIVOS_IGNORAR = ["config.ini", "DESARROLLO.txt"]

     # ... rutas, memoria ...
    cont_ok = 0
    cont_nuevos = 0
    cont_alertas = 0

    # 1. Escaneo actual
    estado_actual = {}

    # 2. Recorre cada ruta de la lista
    for r in ruta:
        # Escanea UNA carpeta y guarda el resultado temporalmente
        resultado_carpeta = mapear_carpeta(r)

        # Mezcla lo que acaba de encontrar con el diccionario general
        estado_actual.update(resultado_carpeta)

        # Aplica el filtrado de archivos
        estado_filtrado = {}
        for archivo, datos in estado_actual.items():
            es_ignorado = False

          # Comprueba si termina en alguna extensión 'prohibida'
            for ext in EXTENSIONES_IGNORAR:
                if archivo.endswith(ext):
                    es_ignorado = True

          # Comprueba si el nombre exacto está en la lista negra
            if os.path.basename(archivo) in ARCHIVOS_IGNORAR:
                es_ignorado = True

            if not es_ignorado:
                estado_filtrado[archivo] = datos

    # 3. Intenta cargar la memoria del pasado
    if not os.path.exists(archivo_memoria):
        # Si NO existe, guarda la primera "foto" y sale
        with open(archivo_memoria, "w") as f:
            json.dump(estado_filtrado, f)
        return

    # 5. El Gran Comparador (La lógica de seguridad)
    try:
    # 5.1. Si existe, lee y compara
        with open(archivo_memoria, "r") as f:
            memoria_pasada = json.load(f)
        for archivo, datos_actuales in estado_filtrado.items():
            if archivo not in memoria_pasada:
                cont_nuevos += 1
                alertas.gritar_al_mundo(f"🆕 NUEVO ARCHIVO DETECTADO: {archivo}", nivel='INFO')
                #Pasa por rayos X
                es_seguro, mensaje_adn = validar_adn(archivo)

                if not es_seguro:
                    alertas.registrar_log(mensaje_adn)
                    alertas.gritar_al_mundo(f'BLOQUEO DE EMERGENCIA: {archivo} por camuflaje de ADN', nivel='CRITICO')

                #BLOQUEO: Lo mueve a cuarentena y lo borra del sitio original
                    os.makedirs('quarantine', exist_ok=True)
                    destino_bloqueo = os.path.join("quarantine", f"BLOQUEADO_{os.path.basename(archivo)}")
                    shutil.move(archivo, destino_bloqueo)  # 'move' lo quita de donde estaba
                    print(f" Archivo neutralizado y movido a cuarentena.")

                    continue

            # Mira el HASH
            elif datos_actuales["hash"] != memoria_pasada[archivo]["hash"]:
                cont_alertas += 1
                nombre_base = os.path.basename(archivo)

                # 1. Registro y grito (llama a alertas.py)

                alertas.registrar_log(f'Modificación detectada en: {archivo}')
                alertas.gritar_al_mundo(f"¡INTRUSO! El archivo {nombre_base} ha sido modificado.", nivel='CRITICO')

                # 2. Protocolo de Decisión (Aquí está la clave)
                if os.path.isfile("DESARROLLO.txt"):
                    # Si es desarrollo, actualiza la bóveda
                    ruta_vault = os.path.join(".gandalf_vault", nombre_base)
                    shutil.copy2(archivo, ruta_vault)
                else:
                    # Si es ataque, llama a seguridad.py
                    seguridad.restaurar_archivo(archivo)

            elif (datos_actuales["tamano"] == memoria_pasada[archivo]["tamano"]) and \
             (datos_actuales["modificado"] == memoria_pasada[archivo]["modificado"]):

                # CHEQUEO DE ADN SECRETO

                if datos_actuales["adn_muestra"] != memoria_pasada[archivo].get("adn_muestra"):
                    cont_alertas += 1
                    alertas.gritar_al_mundo(f"🚨 ¡ALERTA DE SUPLANTACIÓN! El ADN en la posición secreta ha cambiado en {archivo}", nivel='CRITICO')
                  # Aquí dispara la cuarentena
                else:
                    cont_ok += 1
                    continue

            else:
                    cont_ok += 1

        # 5.2 Segundo Comparador: Detecta archivos borrados
        for archivo_viejo in memoria_pasada:
            if archivo_viejo not in estado_filtrado:
                cont_alertas += 1
                alertas.gritar_al_mundo(f"💀 ¡ALERTA! Archivo ELIMINADO: {archivo_viejo}", nivel='ALERTA')
                alertas.registrar_log(f"Archivo desaparecido: {archivo_viejo}")

                seguridad.restaurar_archivo(archivo_viejo)

    except Exception as e:
        print(f"🕵️‍♂️ Gandalf detectó una perturbación en la Fuerza: {e}")
        alertas.registrar_log(f"Error en el escaneo: {e}")

    # 6. Actualiza la memoria
    with open(archivo_memoria, "w") as f:
        json.dump(estado_filtrado, f, indent=4)  # El indent=4 lo hace legible

# Vigila los dispositivos del sistema
def bucle_infinito_vigilancia():
    global usbs_conocidos
    while True:
        ejecutar_gandalf()

        usbs_actuales = seguridad.obtener_unidades_removibles()
        # ... Lógica de comparación de USBs
        # ¿Hay alguno más?
        if len(usbs_actuales) > len(usbs_conocidos):
            nuevos = [u for u in usbs_actuales if u not in usbs_conocidos]
            alertas.lanzar_alerta_telegram(f"⚠️ ¡OJO! Nuevo hardware detectado: {nuevos}")
            usbs_conocidos = usbs_actuales  # Actualiza la memoria

        # ¿Falta alguno?
        elif len(usbs_actuales) < len(usbs_conocidos):
            alertas.lanzar_alerta_telegram("ℹ️ Dispositivo extraído.")
            usbs_conocidos = usbs_actuales

            orden = alertas.leer_mensajes()
            if orden == "/status":
                alertas.lanzar_alerta_telegram("✅ Gandalf está en guardia. Sistema de archivos y Firewall activos.")

        sys.stdout.write(". ")
        sys.stdout.flush()
        time.sleep(TIEMPO_ESPERA)

if __name__ == "__main__":
    print("🛡️ Gandalf ha iniciado su guardia silenciosa...")

    # 1. Activa el servidor Flask
    threading.Thread(target=lambda: servidor_app.run(port=5000, use_reloader=False), daemon=True).start()

    # 2.Inicia variables
    alertas.leer_mensajes()
    usbs_conocidos = seguridad.obtener_unidades_removibles()

    # 3. Lanza el bucle de vigilancia en su Hilo (Daemon)
    threading.Thread(target=bucle_infinito_vigilancia, daemon=True).start()

    # 4. Inicia la bandeja
    hilo_bandeja = threading.Thread(target=tray_icon.iniciar_bandeja, daemon=True)
    hilo_bandeja.start()

    # 5. INTERFAZ (HILO PRINCIPAL)
    # Con ventana.withdraw() en interfaz.py, no sale la ventana al arrancar.
    interfaz.ventana.mainloop()

