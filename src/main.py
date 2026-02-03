from src.scanner import mapear_carpeta  # Importamos tu "habilidad"


def ejecutar_gandalf():
    print("--- 🧙‍♂️ gandalfKey: Vigilancia Iniciada ---")

    ruta_a_vigilar = "./"  # Vigila la carpeta actual del proyecto

    # 1. Escaneamos la carpeta
    resultado = mapear_carpeta(ruta_a_vigilar)

    # 2. Mostramos lo que Gandalf ha visto
    for archivo, huella in resultado.items():
        print(f"Vigilando: {archivo} | Hash: {huella[:10]}...")  # Solo mostramos 10 caracteres del hash


if __name__ == "__main__":
    ejecutar_gandalf()