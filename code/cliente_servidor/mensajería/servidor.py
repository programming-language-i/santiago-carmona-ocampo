import socket
import threading

HOST = "127.0.0.1"
PORT = 8000

# Diccionario para almacenar los clientes activos:
# {conexion: nombre_usuario}
clientes = {}
lock = threading.Lock()


def enviar_mensajes(mensaje_bytes, emisor_conexion=None):
    """Envía un mensaje a todos los clientes conectados, excepto al emisor."""

    # Primero obtenemos una copia de las conexiones.
    # Así no mantenemos el lock mientras hacemos operaciones de red.
    with lock:
        conexiones = [
            conexion
            for conexion in clientes
            if conexion != emisor_conexion
        ]

    conexiones_fallidas = []

    for conexion in conexiones:
        try:
            conexion.sendall(mensaje_bytes)
        except (OSError, ConnectionResetError):
            print("Error al enviar mensaje a un cliente.")
            conexiones_fallidas.append(conexion)

    # Eliminamos las conexiones que ya no funcionan.
    if conexiones_fallidas:
        with lock:
            for conexion in conexiones_fallidas:
                clientes.pop(conexion, None)


def atender_clientes(conexion, direccion):
    """Gestiona la comunicación individual de cada cliente."""

    nombre_usuario = "Desconocido"

    try:
        # El primer mensaje enviado por el cliente debe ser su nombre.
        nombre_bytes = conexion.recv(1024)

        if not nombre_bytes:
            return

        try:
            nombre_usuario = nombre_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            print(f"[!] Nombre inválido recibido desde {direccion}.")
            return

        if not nombre_usuario:
            print(f"[!] Cliente conectado sin nombre desde {direccion}.")
            return

        with lock:
            clientes[conexion] = nombre_usuario

        print(f"[+] ¡{nombre_usuario} se ha conectado desde {direccion}!")

        # Notificar a los demás clientes.
        aviso_ingreso = (
            f"--- {nombre_usuario} se ha unido al chat ---"
        ).encode("utf-8")

        enviar_mensajes(aviso_ingreso, conexion)

        while True:
            datos = conexion.recv(1024)

            if not datos:
                break

            try:
                mensaje_texto = datos.decode("utf-8").strip()
            except UnicodeDecodeError:
                print(f"[!] Mensaje inválido recibido de {nombre_usuario}.")
                continue

            if not mensaje_texto:
                continue

            # Mostrar el mensaje en la consola del servidor.
            print(f"[{nombre_usuario}]: {mensaje_texto}")

            # Enviar el mensaje a los demás clientes.
            mensaje_con_nombre = (
                f"{nombre_usuario}: {mensaje_texto}"
            ).encode("utf-8")

            enviar_mensajes(mensaje_con_nombre, conexion)

    except (ConnectionResetError, BrokenPipeError, OSError):
        print(f"[-] Conexión perdida con {direccion}")

    finally:
        # Eliminar al cliente del diccionario.
        with lock:
            nombre_salida = clientes.pop(conexion, nombre_usuario)

        try:
            conexion.close()
        except OSError:
            pass

        print(f"[-] {nombre_salida} se ha desconectado.")

        # Avisar a los demás clientes.
        aviso_salida = (
            f"--- {nombre_salida} ha abandonado el chat ---"
        ).encode("utf-8")

        enviar_mensajes(aviso_salida)


def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()

        print(
            f"[Servidor iniciado] "
            f"Escuchando en {servidor.getsockname()}"
        )

        try:
            while True:
                conexion, direccion = servidor.accept()

                hilo = threading.Thread(
                    target=atender_clientes,
                    args=(conexion, direccion),
                    daemon=True
                )

                hilo.start()

        except KeyboardInterrupt:
            print("\n[Servidor detenido manualmente]")


if __name__ == "__main__":
    iniciar_servidor()
