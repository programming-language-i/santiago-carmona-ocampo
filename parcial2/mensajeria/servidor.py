import socket # Importar librería para conexiones de red entre el servidor y los clientes.
import sys # Importar librería para acceder a los argumentos que se pasan al ejecutar el programa y controlar su salida.
import threading # Importar librería para ejecutar varios hilos y atender a varios clientes simultáneamente.

from mensajeria.protocolo import enviar_mensaje, recibir_mensaje # Importa funciones para enviar y recibir mensajes 
from mensajeria.registro import RegistroClientes # Importa la clase que administra el registro de clientes conectados


HOST = "127.0.0.1" # Define la dirección IP local para que el servidor acepte conexiones desde el mismo equipo.

registro = RegistroClientes() # objeto para almacenar, buscar, registrar y eliminar los clientes conectados.
lock_envio = threading.Lock() # bloqueo para coordinar los envíos de mensajes y evitar que varios hilos envíen simultáneamente.


def difundir(emisor: str, mensaje: str) -> None: # Define la función para retransmitir un mensaje a los demás clientes.
    texto = f"{emisor}: {mensaje}" # Construye el mensaje que recibirán los demás, incluyendo el nombre del emisor.
    destinatarios = registro.destinatarios(excepto=emisor) # Obtiene la lista de clientes registrados, excluyendo al emisor para que no reciba su propio mensaje.

    with lock_envio: # Activa el bloqueo para coordinar los envíos de mensajes entre los diferentes hilos.
        for nombre, cliente in destinatarios: # Recorre la lista de destinatarios; obtiene el nombre y la conexión de cada cliente.
            try: # bloque para intentar enviar el mensaje y detectar posibles errores.
                enviar_mensaje(cliente, texto) # Envía el mensaje completo al cliente usando la función del protocolo.

            except (OSError, ConnectionError): # Captura errores de red o de conexión que pueden ocurrir durante el envío.
                registro.borrar(nombre, cliente) # Elimina del registro al cliente que presentó el error, siempre que siga siendo la misma conexión.

                try: # Intenta cerrar la conexión del cliente que presentó el error.
                    cliente.close() # Cierra el socket para liberar los recursos de esa conexión.
                except OSError: # Captura un posible error al intentar cerrar el socket.
                    pass # Ignora el error porque la conexión podría estar cerrada previamente.


def atender_cliente( # Define la función que administra la comunicación con un cliente
    cliente: socket.socket, # Recibe el socket que permite comunicarse con el cliente.
    direccion # Recibe la dirección del cliente que se conecta al servidor.
) -> None: # Indica que la función no devuelve un resultado.
    nombre = None # Inicializa el nombre como None porque todavía no se conoce el nombre del cliente.
    registrado = False # Indica que inicialmente el cliente todavía no está registrado.

    try: # Inicia el bloque que contiene las operaciones de comunicación con el cliente.
        # La primera trama contiene el nombre del cliente.
        nombre = recibir_mensaje(cliente) # Recibe el primer mensaje enviado por el cliente, que debe contener su nombre.

        if nombre is None or not nombre.strip(): # Comprueba si la conexión se cerró antes de recibir el nombre o si el nombre está vacío o contiene solo espacios.
            return # Termina la atención de este cliente si el nombre no es válido.

        nombre = nombre.strip() # Elimina los espacios al principio y al final del nombre recibido.

        # Registrar el cliente sin permitir nombres duplicados.
        if not registro.insertar(nombre, cliente): # Intenta registrar al cliente y comprueba si el nombre ya está ocupado.
            try: # Intenta enviar una respuesta indicando que el nombre no está disponible.
                enviar_mensaje(cliente, "ERROR: nombre en uso") # Informa al cliente que debe utilizar otro nombre.
            except OSError: # Captura un posible error de red al enviar la respuesta.
                pass # Ignora el error si no es posible enviar el mensaje.
            return # Termina la atención del cliente rechazado; el bloque finally se ejecutará igualmente.

        registrado = True # Indica que el cliente quedó registrado correctamente.

        enviar_mensaje(cliente, "OK") # Confirma al cliente que su nombre fue aceptado y que puede comenzar a comunicarse.
        print(f"Cliente conectado: {nombre}") # Muestra en la terminal el nombre del cliente que acaba de conectarse.

        # Recibir mensajes hasta que el cliente se desconecte.
        while True: # Mantiene la comunicación activa en un ciclo hasta que el cliente se desconecte o se produzca una interrupción.
            mensaje = recibir_mensaje(cliente) # Espera y recibe el siguiente mensaje enviado por el cliente.

            if mensaje is None: # Comprueba si el cliente cerró la conexión o si ya no se pudo recibir otro mensaje.
                break # Finaliza el ciclo de recepción cuando no quedan mensajes disponibles por recibir.

            difundir(nombre, mensaje) # Retransmite el mensaje recibido a los demás clientes conectados.

    except (OSError, ConnectionError, UnicodeError) as error: # Captura errores de red, conexión o decodificación de texto durante la comunicación.
        print(f"Conexión interrumpida con {nombre}: {error}") # Muestra en la terminal el nombre del cliente y el error que interrumpió la comunicación.

    finally: # Ejecuta las instrucciones de limpieza al terminar, incluso si ocurre un error o se utiliza return.
        # Solo elimina al cliente si sigue siendo el mismo socket.
        if registrado: # Comprueba que este cliente haya sido registrado correctamente antes de intentar eliminarlo.
            registro.borrar(nombre, cliente) # Elimina su registro únicamente si el nombre todavía corresponde a esta conexión.
            print(f"Cliente desconectado: {nombre}") # Informa en la terminal que el cliente se desconectó.

        try: # Intenta cerrar la conexión del cliente.
            cliente.close() # Cierra el socket del cliente y libera los recursos asociados.
        except OSError: # Captura un posible error al cerrar el socket.
            pass # Ignora el error si no se puede cerrar la conexión porque ya está cerrada o presenta un problema.


def main() -> None: # Define la función principal que inicia y mantiene funcionando el servidor.
    if len(sys.argv) != 2: # Comprueba que se haya proporcionado exactamente un argumento al ejecutar el programa: el número del puerto.
        print("Uso: python -m mensajeria.servidor <puerto>") # Muestra la forma correcta de ejecutar el servidor si falta el puerto o sobran argumentos.
        sys.exit(1) # Finaliza el programa indicando que ocurrió un error de ejecución.

    try: # Inicia un bloque para convertir el argumento recibido en un número entero.
        puerto = int(sys.argv[1]) # Obtiene el puerto escrito al ejecutar el programa y lo convierte en un entero.
    except ValueError: # Captura el error que ocurre si el argumento no representa un número entero válido.
        print("Error: el puerto debe ser un número entero.") # Informa que el puerto ingresado no es válido.
        sys.exit(1) # Finaliza el programa porque no puede continuar con un puerto inválido.

    servidor = socket.socket( # Crea un socket que utilizará el servidor para aceptar conexiones.
        socket.AF_INET, # Indica que se utilizará el protocolo de direcciones IPv4.
        socket.SOCK_STREAM # Indica que se utilizará TCP, un protocolo orientado a conexiones.
    ) # Finaliza la creación del socket del servidor.

    servidor.setsockopt( # Configura una opción del socket del servidor.
        socket.SOL_SOCKET, # Indica que la opción corresponde al nivel general del socket.
        socket.SO_REUSEADDR, # Permite reutilizar la dirección local cuando sea posible, facilitando reiniciar el servidor.
        1 # Activa esta opción.
    ) # Finaliza la configuración de la opción del socket.

    try: # Inicia el bloque que contiene las operaciones principales del servidor.
        servidor.bind((HOST, puerto)) # Asocia el socket a la dirección IP local y al puerto seleccionado.
        servidor.listen() # Pone el socket en modo escucha para aceptar conexiones entrantes.

        print(f"Servidor escuchando en {HOST}:{puerto}") # Muestra la dirección IP y el puerto donde está escuchando el servidor.

        while True: # Mantiene el servidor funcionando continuamente para aceptar nuevos clientes.
            cliente, direccion = servidor.accept() # Espera una conexión entrante y devuelve el socket del cliente y su dirección.

            hilo = threading.Thread( # Crea un hilo independiente para atender al cliente recién conectado.
                target=atender_cliente, # Indica que el hilo ejecutará la función encargada de atender al cliente.
                args=(cliente, direccion), # Pasa a la función el socket del cliente y su dirección.
                daemon=True # Configura el hilo como secundario para que no impida terminar el programa cuando finaliza el hilo principal.
            ) # Finaliza la creación del hilo.

            hilo.start() # Inicia el hilo para que comience a atender al cliente mientras el servidor sigue aceptando otras conexiones.

    except KeyboardInterrupt: # Detecta cuando el usuario interrumpe el servidor, normalmente con Ctrl+C.
        print("Servidor detenido.") # Muestra un mensaje indicando que el servidor se está deteniendo.

    except OSError as error: # Captura errores del sistema relacionados con el socket, el puerto o las conexiones.
        print(f"Error en el servidor: {error}") # Muestra el mensaje del error ocurrido en el servidor.

    finally: # Ejecuta la limpieza final al salir del bloque try, incluso si ocurre un error.
        servidor.close() # Cierra el socket principal del servidor y libera los recursos asociados.


if __name__ == "__main__": # Comprueba si este archivo se está ejecutando directamente como programa principal.
    main() # Ejecuta la función principal para iniciar el servidor.