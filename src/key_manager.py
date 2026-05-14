import keyring
import logging

logger = logging.getLogger(__name__)

def keep_secret(key_name, value):
    keyring.set_password("Gandalf_Guard", key_name, value)

def get_secret(key_name):
    secret = keyring.get_password("Gandalf_Guard", key_name)
    # Verifica si el secreto existe antes de entregarlo
    if secret is None:
        # Aquí decidimos qué hacer: ¿Lanzamos un aviso? ¿Devolvemos un error controlado?
        logger.critical(f"⚠️ ¡Alerta! No se encontró la clave: {key_name}")
        return False

    return secret

