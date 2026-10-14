import socket


def enviar_mensaje(sock: socket.socket, mensaje: str) -> None:
    """
    Sirve para enviar un mensaje de texto mediante un socket TCP.

    """
    cuerpo = mensaje.encode("utf-8")

    longitud = len(cuerpo).to_bytes(4, byteorder="big")

    trama = longitud + cuerpo

    sock.sendall(trama)


def recibir_exacto(sock: socket.socket, cantidad: int) -> bytes | None:
    """
    Recibe exactamente la cantidad de bytes solicitada.
    
    """
    datos = bytearray()

    while len(datos) < cantidad:
        bloque = sock.recv(cantidad - len(datos))

        if bloque == b"":
            return None

        datos.extend(bloque)

    return bytes(datos)


def recibir_mensaje(sock: socket.socket) -> str | None:
    """
    Recibe un mensaje completo siguiendo el protocolo de framing.

    Primero lee los 4 bytes de longitud y después el cuerpo
    completo del mensaje, que está codificado en UTF-8.
    """
    prefijo = recibir_exacto(sock, 4)

    if prefijo is None:
        return None

    longitud = int.from_bytes(prefijo, byteorder="big")

    cuerpo = recibir_exacto(sock, longitud)

    if cuerpo is None:
        return None

    return cuerpo.decode("utf-8")