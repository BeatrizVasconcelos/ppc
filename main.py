from threading import Thread
from random import randint
from time import time
import classes

left = []
right = []


# Função da Thread Bridge
def thread_bridge():
    bridge = classes.Bridge()
    print(bridge)
    while(True):
        pass


def thread_queue():
    num_cars = 0
    while(num_cars < 100):
        car = classes.Carro()
        # Gera uma direção (0 = esquerda, 1 = direita) aleatoriamente
        direction = randint(0, 1)
        if (direction):
            right.append(car)
        else:
            left.append(car)
        # Gera um tempo de chegada aleatório
        waiting_time = randint(2, 6)
        time.sleep(waiting_time)


# Código que será executado
def main():
    bridge = Thread(target=thread_bridge)
    bridge.start()
    queue = Thread(target=thread_queue)
    queue.start()


if(__name__ == '__main__'):
    main()
