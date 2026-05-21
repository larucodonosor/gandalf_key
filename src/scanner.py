import os
import sys
import integrity_utils
import backup_manager
import logging

logger = logging.getLogger(__name__)

def map_folder(directory_path):
    # Escanea una carpeta y devuelve un diccionario {archivo: hash}.
    registry = {}

    # Verificación de seguridad para evitar errores en el bucle principal
    if not os.path.exists(directory_path):
        logger.warning(f"El escáner intentó acceder a una ruta inexistente: {directory_path}")
        return None

    try:
        # Lista el contenido íntegro de la carpeta
        for file_name in os.listdir(directory_path):
            full_path = os.path.join(directory_path, file_name)
            # Ignora subcarpetas, solo procesa archivos
            if not os.path.isfile(full_path):
                continue

        file_hash = integrity_utils.get_file_hash(full_path)
        if file_hash: # Lo añade si se pudo leer correctamente
            stats = os.stat(full_path)
            file_id = os.path.abspath(full_path)  # ID única

            registry[file_id] = {
                'hash': file_hash,
                'size': stats.st_size,
                'modified_at': stats.st_mtime, #Guarda la fecha e formato máquina
                'dna_sample': integrity_utils.get_dna_sample(full_path), # adn_muestra
            }
    except Exception as e:
        logger.error(f"Error crítico durante el mapeo de la carpeta {directory_path}: {e}")

    return registry
