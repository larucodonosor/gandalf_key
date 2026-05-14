import time
import requests
import logging

# Para usar el archivo de logs
logger = logging.getLogger(__name__)

def retry_request(func, *args, **kwargs):
    # Ejecuta cualquier llamada de red.
    max_attemps = 3
    wait_time = 5

    for attemp in range(max_attemps):
        try:
            response = func(*args, **kwargs)
            # Si es un código 200 (éxito), devuelve la respuesta
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logging.warning(f"Fallo de conexión (intento {attemp+1}): {e}")
            if attemp < max_attemps - 1:
                time.sleep(wait_time)
                wait_time *= 2
            else:
                logging.critical("Se agotaron los reintentos de red, comprueba la conexión e inténtalo de nuevo más tarde")
                raise e # Si hay fallo total, avisa al programa