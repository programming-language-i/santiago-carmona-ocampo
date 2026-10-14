import socket
import threading


class RegistroClientes:
    def __init__(self):
        self.clientes = {}
        self.lock = threading.Lock()

    def insertar(self, nombre: str, cliente: socket.socket) -> bool:
        with self.lock:
            if nombre in self.clientes:
                return False

            self.clientes[nombre] = cliente
            return True

    def buscar(self, nombre: str) -> socket.socket | None:
        with self.lock:
            return self.clientes.get(nombre)

    def borrar(self, nombre: str) -> None:
        with self.lock:
            self.clientes.pop(nombre, None)

    def destinatarios(
        self, excepto: str | None = None
    ) -> list[tuple[str, socket.socket]]:
        with self.lock:
            return [
                (nombre, cliente)
                for nombre, cliente in self.clientes.items()
                if nombre != excepto
            ]