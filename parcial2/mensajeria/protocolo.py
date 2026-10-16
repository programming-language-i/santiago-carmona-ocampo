import socket #Importar librería socket para la comunicación en red


def enviar_mensaje(sock: socket.socket, mensaje: str) -> None:#Función para enviar un mensaje a través de un socket TCP
    """
    Sirve para enviar un mensaje de texto mediante un socket TCP.

    """
    cuerpo = mensaje.encode("utf-8") # Convierte el texto en bytes usando UTF-8 y los guarda en "cuerpo"

    longitud = len(cuerpo).to_bytes(4, byteorder="big")# Calcula la longitud del mensaje en bytes y la convierte a 4 bytes

    trama = longitud + cuerpo # Une la longitud del mensaje y el contenido en una sola secuencia de bytes 

    sock.sendall(trama) #Envía la trama completa a través del socket.


def recibir_exacto(sock: socket.socket, cantidad: int) -> bytes | None: # Función para recibir una cantidad exacta de bytes desde un socket TCP
    """
    Recibe exactamente la cantidad de bytes solicitada.
    
    """
    datos = bytearray() # Crea un espacio vacío donde se acumulan los bytes recibidos.

    while len(datos) < cantidad: # Ciclo que se repite hasta que se reciben todos los bytes solicitados.
        bloque = sock.recv(cantidad - len(datos)) #Recibe bytes de la conexión y los guarda temporalmente en bloque.

        if bloque == b"": # Si no se reciben más bytes, significa que la conexión se ha cerrado.
            return None

        datos.extend(bloque) # Agrega los bytes recibidos al espacio de almacenamiento de datos.

    return bytes(datos) # Convierte el bytearray a bytes y lo devuelve.


def recibir_mensaje(sock: socket.socket) -> str | None: # Función para recibir un mensaje completo siguiendo el protocolo de framing.
    """
    Recibe un mensaje completo siguiendo el protocolo de framing.

    Primero lee los 4 bytes de longitud y después el cuerpo
    completo del mensaje, que está codificado en UTF-8.
    """
    prefijo = recibir_exacto(sock, 4) # Lee los primeros 4 bytes que indican la longitud del mensaje.

    if prefijo is None: # Si no se reciben los 4 bytes, significa que la conexión se ha cerrado o hubo un error.
        return None

    longitud = int.from_bytes(prefijo, byteorder="big") # Convierte los 4 bytes de longitud a un entero que representa la cantidad de bytes del mensaje.

    cuerpo = recibir_exacto(sock, longitud) # Lee el cuerpo del mensaje según la longitud obtenida previamente.

    if cuerpo is None: # Si no se reciben todos los bytes del cuerpo, significa que la conexión se ha cerrado o hubo un error.
        return None

    return cuerpo.decode("utf-8") # Decodifica los bytes del cuerpo a una cadena de texto usando UTF-8 y la devuelve.