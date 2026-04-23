from cryptography.fernet import Fernet
import os


# Carga la clave maestra o la genera si no existe
def load_or_create_key():
    key_path = "config/sys_cache.bin"
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

    with open(file_path, 'rb') as file:
        file_data = file.read()

    return fernet.encrypt(file_data)


def decrypt_file(file_path):
    # Descifra datos usando la clave maestra.
    key = load_or_create_key()
    fernet = Fernet(key)
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    return fernet.decrypt(encrypted_data)
