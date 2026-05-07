import time
import requests
import logging

# Configuración para usar el archivo de logs
logging.basicConfig(filename='network_activity.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def retry_request(func, *args, **kwargs):
    # Ejecuta cualquier llamada de red.
    max_intentos = 3
    espera = 5

    for intento in range(max_intentos):
        try:
            response = func(*args, **kwargs)
            # Si es un código 200 (éxito), devuelve la respuesta
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logging.warning(f"Fallo de conexión (intento {intento+1}): {e}")
            if intento < max_intentos - 1:
                time.sleep(espera)
                espera *= 2
            else:
                logging.error("Se agotaron los reintentos de red, comprueba la conexión e inténtalo de nuevo más tarde")
                raise e # Si hay fallo total, avisa al programa