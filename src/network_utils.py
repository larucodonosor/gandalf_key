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
            result = func(*args, **kwargs)

            if hasattr(result, 'raise_for_status'):
                result.raise_for_status()

            return result

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
            logger.warning(f"Fallo en llamada de red (Intento {current_attempt}/{max_attempts}): {e}")
            # Si ya es el último intento de todos, avisa al sistema
            if current_attempt == max_attempts:
                logger.critical("🚨 Se agotaron todos los reintentos de red. Comprueba la conexión.")
                raise e

            # LOGICA DE ESPERA DINÁMICA
            if current_attempt == 5:
                # 300 segundos = 5 minutos exactos de tregua
                next_wait = 300
                logger.warning(
                    f"⚠ Falla crítica de red (Intento 5). Gandalf entra en reposo. Próximo intento en 5 min.")
            elif current_attempt == 6:
                # Otros 5 minutos antes del último cartucho
                next_wait = 300
                logger.warning(f"La red sigue caída (Intento 6). Último intento desesperado en 5 min.")
            else:
                # Progresión geométrica para intentos 1, 2, 3 y 4 (5s, 10s, 20s, 40s...)
                next_wait = wait_time
                wait_time *= 2  # Duplica el multiplicador para el próximo giro

            # El hilo duerme el tiempo exacto calculado
            time.sleep(next_wait)