import socket
import threading


class RegistroClientes:
    """
    crea una clase que administra los clientes.
    
    """
    def __init__(self):#repara los datos cuando se crea un objeto de esta clase.

        self.clientes = {}#crea un diccionario vacío donde se guardan los clientes. El nombre es la clave y el socket es el valor.
        self.lock = threading.Lock()#crea un bloqueo para evitar que varios hilos modifiquen el registro al mismo tiempo.

    def insertar(self, nombre: str, cliente: socket.socket) -> bool: #Registrar cliente
        with self.lock:#bloquea temporalmente el registro mientras se realiza la operación.
            if nombre in self.clientes: #comprueba si ese nombre ya existe.
                return False #si ya existe, no registra al cliente.

            self.clientes[nombre] = cliente #si no existe, guarda su nombre y conexión.
            return True

    def buscar(self, nombre: str) -> socket.socket | None:# busca un cliente por su nombre.
        with self.lock:
            return self.clientes.get(nombre)

    def borrar(self, nombre: str) -> None: #elimina un cliente del registro.
        with self.lock:
            self.clientes.pop(nombre, None)

    def destinatarios( #Obtiene los clientes a quienes enviar un mensaje, excluyendo opcionalmente al emisor.
        self, excepto: str | None = None
    ) -> list[tuple[str, socket.socket]]:
        with self.lock:
            return [
                (nombre, cliente)
                for nombre, cliente in self.clientes.items()
                if nombre != excepto
            ]