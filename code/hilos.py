import threading
import time


def leer_sensor(id_sensor, temperatura):
    """Función que ejecuta cada hilo para simular un sensor."""
    for _ in range(3):
        print(f"Sensor {id_sensor} - Temperatura: {temperatura}°C")
        time.sleep(1)


def main():
    datos_sensores = [
        (1, 30),
        (2, 35),
        (3, 50),
        (4, 40),
        (5, 45)
    ]

    hilos = []

    for id_sensor, temperatura in datos_sensores:
        hilo = threading.Thread(
            target=leer_sensor,
            args=(id_sensor, temperatura)
        )

        hilos.append(hilo)
        hilo.start()

    # Esperar a que todos los hilos terminen
    for hilo in hilos:
        hilo.join()

    print("¡Todos los sensores han finalizado!")


if __name__ == "__main__":
    main()
```
