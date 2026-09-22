import threading 
import time


def imprimir mensaje():
    for i in range(5):
        print("hello")
        time.sleep(1)


def main():
    thread = threading.thread(target=imprimir_mensaje)

    thread2 = threading.thread(target=imprimir_mensaje)

    thread3 = threading.thread(target=imprimir_mensaje)


def main():
    thread = threading.Thread()

if __name__ == "__main__":
    main()