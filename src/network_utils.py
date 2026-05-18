import time
import requests
import logging

# Para usar el archivo de logs
logger = logging.getLogger(__name__)

def retry_request(func, *args, **kwargs):
    # Ejecuta cualquier llamada de red.
    max_attempts = 7
    wait_time = 5

    for attempt in range(max_attempts):
        current_attempt = attempt + 1
        try:
            response = func(*args, **kwargs)
            # Si es un código 200 (éxito), devuelve la respuesta
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if current_attempt == 5:
                # El 5º falló, el 6º esperará 5 minutos (300 segundos)
                next_wait = 420
                logger.warning(
                    f" Falla crítica de red (Intento 5). Gandalf entrará en reposo. Próximo intento en 5 min: {e}")
            elif current_attempt == 6:
                # El 6º falló, el 7º esperará otros 5 minutos
                next_wait = 600
                logger.warning(f" La red sigue caída (Intento 6). Último intento en otros 5 min: {e}")
            else:
                # Intentos del 1 al 4, aplican la progresión geométrica clásica (5s, 10s, 20s, 40s...)
                next_wait = wait_time
            logger.warning(f"Fallo de conexión (intento {attempt+1}): {e}")
            if attempt < max_attempts - 1:
                time.sleep(next_wait)
            if current_attempt < 5:
                wait_time *= 2
            else:
                logger.critical("Se agotaron los reintentos de red, comprueba la conexión e inténtalo de nuevo más tarde")
                raise e # Si hay fallo total, avisa al programa