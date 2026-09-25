
# PARTE B — Predecir salida

# B1. ¿Cuánto tarda?

import threading
import time


def tarea(n):
    time.sleep(1)


inicio = time.perf_counter()

for i in range(3):
    hilo = threading.Thread(target=tarea, args=(i,))
    hilo.start()
    hilo.join()  # Espera a que el hilo termine antes de continuar.


print(f"{time.perf_counter() - inicio:.1f} s")

# Salida aproximada: 3 segundos, ya que cada tarea tarda 1 segundo, como se usa join() después de cada start(), esperamos a que termine cada hilo antes de continuar.


# B2. Daemon con finally

import threading
import time


def guardar():
    try:
        time.sleep(2)
        print("guardado")
    finally:
        print("archivo cerrado")


threading.Thread(target=guardar, daemon=True).start()

time.sleep(0.5)

print("fin")

# SALIDA ESPERADA: fin, ya que el hilo necesita 2 segundos para terminar el sleep() y el programa principal solamente espera 0.5 segundos para despues imprimir "fin"

from concurrent.futures import ThreadPoolExecutor


def dividir(a, b):
    return a / b


with ThreadPoolExecutor() as pool:
    futuro = pool.submit(dividir, 1, 0)

print("listo")

# SALIDA: "listo"

# B4. Reiniciar un hilo

import threading


hilo = threading.Thread(target=print, args=("hola",))

hilo.start()
hilo.join()

print(hilo.is_alive())



# B5. Procesos y una lista global


import multiprocessing


resultados = []


def calcular(n):
    resultados.append(n * n)


if __name__ == "__main__":

    procesos = [
        multiprocessing.Process(target=calcular, args=(n,))
        for n in range(4)
    ]

    for p in procesos:
        p.start()

    for p in procesos:
        p.join()

    print(resultados)

    # SALIDA:[] ya que, Aunque "resultados" es una variable global, cada procesotiene su propio espacio de memoria.



# B6. Estado por instancia y por clase

import threading


class Contador(threading.Thread):

    # ATRIBUTO DE CLASE: Todas las instancias de Contador comparten esta lista.
    eventos = []

    def __init__(self, nombre):
        super().__init__(name=nombre)

        # ATRIBUTO DE INSTANCIA: Cada objeto tiene su propio "total".
        self.total = 0

    def run(self):

        for _ in range(3):

            # Cada objeto modifica su propio total.
            self.total += 1

            # "eventos" pertenece a la clase, por lo que ambos
            # hilos agregan elementos a la misma lista.
            self.eventos.append(self.name)


a = Contador("a")
b = Contador("b")


for h in (a, b):
    h.start()


for h in (a, b):
    h.join()


print(a.total, b.total, len(a.eventos))

# SALIDA: 3 3 6, ya que "a" y "b" tienen cada uno su propio atributo total:
# a.total = 3
# b.total = 3
