from cryptography.fernet import Fernet
import os
import logging

logger=logging.getLogger(__name__)


# Carga la clave maestra o la genera si no existe
def load_or_create_key():
    config_dir= 'config'
    key_path = os.path.join(config_dir, "sys_cache.bin")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

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
        logger.error(f'Error de ecriptado: {e}')
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
        logger.error(f'Error de decriptado: {e}')
        return None