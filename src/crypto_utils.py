from cryptography.fernet import Fernet
import os
import sys
import logging

logger=logging.getLogger(__name__)

# Estandariza las rutas tanto para desarrollo como producción
def get_secure_key_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_dir = os.path.join(base_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "sys_cache.bin")

# Carga la clave maestra o la genera si no existe
def load_or_create_key():
    key_path = get_secure_key_path()

    if os.path.exists(key_path):
        with open(key_path, 'rb') as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
        return key

def encrypt_file(file_path):
    # Cifra un archivo y devuelve los datos cifrados.
    key = load_or_create_key()
    fernet = Fernet(key)

    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
        return fernet.encrypt(file_data)
    except Exception as e:
        logger.error(f'Error de ecriptado en el archivo {file_path}: {e}')
        return None

def decrypt_file(file_path):
    # Descifra datos usando la clave maestra.
    key = load_or_create_key()
    fernet = Fernet(key)
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        return fernet.decrypt(encrypted_data)
    except Exception as e:
        logger.error(f'Error de decriptado en el archivo {file_path}: {e}')
        return None