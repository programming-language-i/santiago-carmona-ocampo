import socket
import sys
import threading

from mensajeria.protocolo import enviar_mensaje, recibir_mensaje
from mensajeria.registro import RegistroClientes


HOST = "127.0.0.1"

registro = RegistroClientes()
lock_envio = threading.Lock()


def difundir(emisor: str, mensaje: str) -> None:
    texto = f"{emisor}: {mensaje}"
    destinatarios = registro.destinatarios(excepto=emisor)

    # Evita que dos hilos mezclen las tramas enviadas a un cliente.
    with lock_envio:
        for nombre, cliente in destinatarios:
            try:
                enviar_mensaje(cliente, texto)
            except OSError:
                # Si el envío falla, se elimina al cliente desconectado.
                registro.borrar(nombre)
                try:
                    cliente.close()
                except OSError:
                    pass


def atender_cliente(cliente: socket.socket, direccion) -> None:
    nombre = None
    registrado = False

    try:
        # La primera trama contiene el nombre del cliente.
        nombre = recibir_mensaje(cliente)

        if nombre is None or not nombre:
            return

        if not registro.insertar(nombre, cliente):
            enviar_mensaje(cliente, "ERROR: nombre en uso")
            return

        registrado = True
        enviar_mensaje(cliente, "OK")
        print(f"Cliente conectado: {nombre}")

        while True:
            mensaje = recibir_mensaje(cliente)

            if mensaje is None:
                break

            difundir(nombre, mensaje)

    except (OSError, ConnectionError, UnicodeError) as error:
        print(f"Conexión interrumpida con {nombre}: {error}")

    finally:
        # Solo se elimina el nombre si esta conexión lo registró.
        if registrado:
            registro.borrar(nombre)
            print(f"Cliente desconectado: {nombre}")

        try:
            cliente.close()
        except OSError:
            pass


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python -m mensajeria.servidor <puerto>")
        sys.exit(1)

    puerto = int(sys.argv[1])

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor.bind((HOST, puerto))
        servidor.listen()

        print(f"Servidor escuchando en {HOST}:{puerto}")

        while True:
            cliente, direccion = servidor.accept()

            hilo = threading.Thread(
                target=atender_cliente,
                args=(cliente, direccion),
                daemon=True,
            )
            hilo.start()

    except KeyboardInterrupt:
        print("Servidor detenido.")

    finally:
        servidor.close()


if __name__ == "__main__":
    main()