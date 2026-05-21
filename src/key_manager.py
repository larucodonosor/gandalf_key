import keyring
import logging

logger = logging.getLogger(__name__)

def keep_secret(key_name, value):
    try:
        safe_value = value if value is not None else ""
        keyring.set_password("Gandalf_Guard", key_name, safe_value)
    except Exception as e:
        logger.error(f"Fallo físico al intentar escribir en el llavero del S.O: {e}")
def get_secret(key_name):
    try:
        secret = keyring.get_password("Gandalf_Guard", key_name)
    except Exception as e:
        logger.error(f"Error de acceso al llavero del Sistema Operativo: {e}")
        return ""

    # Verifica si el secreto existe antes de entregarlo
    if secret is None:
        # Aquí decidimos qué hacer: ¿Lanzamos un aviso? ¿Devolvemos un error controlado?
        logger.critical(f"⚠ ¡Alerta! No se encontró la clave: {key_name}")
        return False

    return secret

