import os
import integrity_utils
import backup_manager

def mapear_carpeta(ruta_directorio):
    # Escanea una carpeta y devuelve un diccionario {archivo: hash}.
    registro = {}
    # Lista el contenido íntegro de la carpeta
    for nombre_archivo in os.listdir(ruta_directorio):
        ruta_completa = os.path.join(ruta_directorio, nombre_archivo)

    # Solo procesa si es un archivo (ignoramos subcarpetas por ahora)
        if os.path.isfile(ruta_completa) or not backup_manager.is_treasure_extension(ruta_completa):
            continue

    huella = integrity_utils.get_file_hash(ruta_completa)
    if huella: # Lo añade si se pudo leer correctamente
        stats = os.stat(ruta_completa)
        ruta_dni = os.path.abspath(ruta_completa)  # ID única

        registro[ruta_dni] = {
            'hash': huella,
            'tamano': stats.st_size,
            'modificado': stats.st_mtime, #Guarda la fecha e formato máquina
            'adn_muestra': integrity_utils.obtener_muestra_adn(ruta_completa)
        }

        return registro
