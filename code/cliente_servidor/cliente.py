import socket
import threading

HOST = "127.0.0.1"
PORT = 8000


def recibir_mensajes(conexion):
    """Recibe y muestra los mensajes enviados por el servidor."""

    while True:
        try:
            datos = conexion.recv(1024)

            if not datos:
                print("\n[!] El servidor cerró la conexión.")
                break

            mensaje = datos.decode("utf-8")
            print(f"\n{mensaje}")

        except (ConnectionResetError, BrokenPipeError, OSError):
            print("\n[!] Se perdió la conexión con el servidor.")
            break


def iniciar_cliente():
    nombre_usuario = input("Ingrese su nombre: ").strip()

    if not nombre_usuario:
        print("El nombre no puede estar vacío.")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((HOST, PORT))

            print(f"\n[+] Conectado al servidor {HOST}:{PORT}")

            # El servidor espera el nombre como primer mensaje.
            cliente.sendall(nombre_usuario.encode("utf-8"))

            # Hilo encargado de recibir mensajes.
            hilo_receptor = threading.Thread(
                target=recibir_mensajes,
                args=(cliente,),
                daemon=True
            )

            hilo_receptor.start()

            print("Escriba sus mensajes.")
            print("Escriba 'salir' para desconectarse.\n")

            while True:
                mensaje = input()

                if mensaje.lower() == "salir":
                    break

                if not mensaje.strip():
                    continue

                try:
                    cliente.sendall(mensaje.encode("utf-8"))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    print("[!] No se pudo enviar el mensaje.")
                    break

    except ConnectionRefusedError:
        print("[!] No se pudo conectar al servidor.")
        print("    Verifique que el servidor esté ejecutándose.")

    except OSError as error:
        print(f"[!] Error de conexión: {error}")

    finally:
        print("[+] Cliente desconectado.")


if __name__ == "__main__":
    iniciar_cliente()
