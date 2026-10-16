import socket # Importa la librería para trabajar con conexiones de red y sockets de los clientes.
import threading # Importa la librería para trabajar con varios hilos de ejecución.

class RegistroClientes: # Define la clase encargada de administrar los clientes conectados al servidor.
    """Administra los clientes conectados al servidor.""" # Describe la función principal de la clase.

    def __init__(self): # Es el método constructor que Se ejecuta automáticamente cuando se crea un objeto de la clase.
        self.clientes = {} # Crea un diccionario vacío donde se guardan los clientes conectados, usando el nombre como clave y el socket como valor.
        self.lock = threading.Lock() # Crea un bloqueo para proteger el diccionario cuando varios hilos intentan acceder a él al mismo tiempo.

    def insertar(self, nombre: str, cliente: socket.socket) -> bool: # Define el método para registrar un cliente; recibe su nombre y su conexión, y devuelve True o False.
        with self.lock: # Activa el bloqueo para proteger las operaciones que se realizan dentro de este bloque.
            if nombre in self.clientes: # Comprueba si el nombre ya existe en el diccionario de clientes.
                return False # Si el nombre ya está registrado, rechaza el registro y devuelve False.

            self.clientes[nombre] = cliente # Si el nombre no existe, guarda el nombre y la conexión del cliente en el diccionario.
            return True # Indica que el cliente fue registrado correctamente.

    def buscar(self, nombre: str) -> socket.socket | None: # Define el método para buscar un cliente por su nombre; devuelve su conexión o None si no existe.
        with self.lock: # Protege el acceso al diccionario mientras se realiza la búsqueda.
            return self.clientes.get(nombre) # Busca el nombre y devuelve su conexión si existe; de lo contrario, devuelve None.

    def borrar( # Define el método encargado de eliminar un cliente del registro.
        self, # Representa el objeto actual de la clase.
        nombre: str, # Recibe el nombre del cliente que se quiere eliminar.
        cliente_esperado: socket.socket | None = None # Recibe opcionalmente la conexión que se espera eliminar; por defecto, no se especifica ninguna.
    ) -> None: # Indica que el método no devuelve ningún resultado.
        with self.lock: # Activa el bloqueo para proteger la comprobación y eliminación del cliente.
            cliente_actual = self.clientes.get(nombre) # Busca la conexión que está registrada actualmente con ese nombre.

            if cliente_actual is None: # Comprueba si el nombre no está registrado.
                return # Si no existe el cliente, termina el método sin realizar cambios.

            if ( # Inicia una condición para comprobar si la conexión registrada es la que se esperaba eliminar.
                cliente_esperado is not None # Comprueba que se haya proporcionado una conexión esperada.
                and cliente_actual is not cliente_esperado # Comprueba si la conexión actual es diferente de la conexión esperada.
            ): # Finaliza la condición de comprobación.
                return # Si las conexiones son diferentes, cancela la eliminación para no borrar el registro de otro cliente.

            self.clientes.pop(nombre, None) # Elimina el nombre y su conexión del diccionario; si el nombre no existe, no genera un KeyError.

    def destinatarios( # Define el método encargado de obtener los clientes que recibirán un mensaje.
        self, # Representa el objeto actual de la clase.
        excepto: str | None = None # Recibe opcionalmente el nombre del cliente que debe excluirse de la lista.
    ) -> list[tuple[str, socket.socket]]: # Indica que devuelve una lista de tuplas con el nombre y la conexión de cada cliente seleccionado.
        with self.lock: # Protege el acceso al diccionario mientras se prepara la lista de destinatarios.
            return [ # Crea y devuelve una lista nueva con los clientes que cumplen la condición.
                (nombre, cliente) # Agrega una tupla que contiene el nombre y la conexión del cliente.
                for nombre, cliente in self.clientes.items() # Recorre todos los nombres y conexiones almacenados en el diccionario.
                if nombre != excepto # Incluye al cliente solo si su nombre es diferente del nombre que se desea excluir.
            ] # Finaliza la lista de destinatarios.