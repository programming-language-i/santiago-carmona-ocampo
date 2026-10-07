import socket 

with socket.socket(socket.AF_INET, socket. SOCK_STREAM) as cliente: 
    cliente.connect(('localhost', 5000)) 
    mensaje = 'Hola, servidor!' 
    cliente.sendall(mensaje.encode()) 
    respuesta = cliente.recv(1024) 
    print('Respuesta del servidor:', respuesta.decode()) 
    tiempo = 0.5  # Tiempo de espera en segundos
    getattr(cliente, 'settimeout')(tiempo)  # Establecer el tiempo de espera
    variable = cliente.recv(1024)  # Intentar recibir datos
    print('Variable recibida:', variable.decode())  # Imprimir la variable recibida,
    donde se espera que sea 'variable' enviada por el servidor.
    while True:
        try:
            variable = cliente.recv(1024)  # Intentar recibir datos
            if not variable:
                break  # Salir del bucle si no hay más datos
            print('Variable recibida:', variable.decode())  # Imprimir la variable recibida
        except socket.timeout:
            print('No se recibió ninguna variable en el tiempo de espera.')
            break  # Salir del bucle si se alcanza el tiempo de espera
            se espera que el servidor envíe la variable 'variable' después de enviar la respuesta inicial.
            de esta manera, el cliente puede recibir y mostrar la variable enviada por el servidor, o manejar el caso en que no se reciba ninguna variable dentro del tiempo de espera especificado.
            resumen: El cliente se conecta al servidor, envía un mensaje, recibe una respuesta y luego intenta recibir una variable adicional del servidor, manejando el caso en que no se reciba ninguna variable dentro de un tiempo de espera especificado.
            where: El cliente se conecta al servidor, envía un mensaje, recibe una respuesta y luego intenta recibir una variable adicional del servidor, manejando el caso en que no se reciba ninguna variable dentro de un tiempo de espera especificado.
            try:
                variable = cliente.recv(1024)  # Intentar recibir datos
                if not variable:
                    break  # Salir del bucle si no hay más datos
                print('Variable recibida:', variable.decode())  # Imprimir la variable recibida