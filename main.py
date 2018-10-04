from threading import Thread
from threading import Condition
from random import randint
import time
from collections import deque
import numpy as np
import classes

left = deque([])
right = deque([])
bridge = classes.Bridge()
waiting_left = []
waiting_right = []
timing = 0
program_end = False
MAX_CARS = 100


# Função da Thread Bridge
def thread_bridge(cv_bridge, cv_queue):
    num_cars = 0
    total_cars = 0
    global bridge
    while(True):
        print('Bridge direction: {}'.format(bridge.direction))
        print('Same direction crossed cars: {}'.format(num_cars))
        # Espera até que um carro entre na fila direita e,
        # quando entra, o coloca na ponte
        if(bridge.direction == 'right'):
            with(cv_queue):
                while(len(right) == 0):
                    print('Waiting right queue car')
                    cv_queue.wait()
            car, timing = right.popleft()
            waiting_right.append(time.time() - timing)
            print('Right queue car got into the bridge')
        # Espera até que um carro entre na fila esquerda e,
        # quando entra, o coloca na ponte
        else:
            with(cv_queue):
                while(len(left) == 0):
                    print('Waiting left queue car')
                    cv_queue.wait()
            car, timing = left.popleft()
            waiting_left.append(time.time() - timing)
            print('Left queue car got into the bridge')
        # Quando um carro é inserido na ponte, a thread bridge
        # notifica a thread remove_cars
        with(cv_bridge):
            # Tupla com o carro e seu tempo de chegada
            lil_tuple = (car, time.time())
            # Insere o carro e seu tempo de chegada
            bridge.vehicles.append(lil_tuple)
            cv_bridge.notify_all()
        num_cars += 1
        total_cars += 1
        print('Same direction crossed cars: {}'.format(num_cars))
        print('Cars on the bridge: {}'.format(len(bridge.vehicles)))
        time.sleep(2)
        if(num_cars >= 5):
            with(cv_bridge):
                while(len(bridge.vehicles) > 0):
                    print('Waiting bridge to be cleared')
                    cv_bridge.wait()
            bridge.change_direction()
            print('Bridge changed direction')
            num_cars = 0
        if(total_cars >= MAX_CARS):
            print('Thread bridge encerrou')
            break


# Função que gera carros
def thread_queue(cv_queue):
    directions = [0, 1]
    qt_right = 0
    qt_left = 0
    while(True):
        car = classes.Car()
        # Gera uma direção (0 = esquerda, 1 = direita) aleatoriamente
        if(len(directions) == 0):
            break
        i = randint(0, len(directions) - 1)
        direction = directions[i]
        tup = (car, time.time())
        if(direction == 1):
            right.append(tup)
            qt_right += 1
            print('Car inserted on right queue\n')
            if(qt_right >= (MAX_CARS / 2)):
                try:
                    directions.remove(1)
                except ValueError:
                    pass
        else:
            left.append(tup)
            qt_left += 1
            print('Car inserted on left queue\n')
            if(qt_left >= (MAX_CARS / 2)):
                try:
                    directions.remove(0)
                except ValueError:
                    pass
        # Notifica todas as threads após inserir um carro em uma das filas
        with(cv_queue):
            cv_queue.notify_all()
        # Gera um tempo de chegada aleatório
        waiting_time = randint(2, 6)
        time.sleep(waiting_time)
    print('Thread queue encerrou')


# Função que retira os carros da ponte, após passados 10 segundos de travessia
def thread_remove_cars(cv_bridge):
    removed_cars = 0
    while(True):
        # Se não houver carros, a thread dorme
        with(cv_bridge):
            while(len(bridge.vehicles) == 0):
                print('Empty bridge')
                cv_bridge.notify_all()
                cv_bridge.wait()
        crossing_time = bridge.vehicles[0][0].time_to_pass
        while((time.time() - bridge.vehicles[0][1]) < crossing_time):
            pass
        bridge.vehicles.popleft()
        with(cv_bridge):
            cv_bridge.notify_all()
        removed_cars += 1
        print('Car removed from {} direction\n\n'.format(bridge.direction))
        if(removed_cars >= MAX_CARS):
            print('Thread remove cars encerrou')
            break


def thread_time_calculator(cv_bridge):
    global timing
    while(True):
        while(len(bridge.vehicles) == 0 and not program_end):
            with(cv_bridge):
                cv_bridge.wait()

        init = time.time()
        while(len(bridge.vehicles) >= 1 and not program_end):
            with(cv_bridge):
                cv_bridge.wait()
        using_time = time.time() - init
        timing += using_time
        if(program_end):
            print('Thread time calculator encerrou')
            break


def results(program_time):
    program_time = time.time()
    print('Número total de carros que atravessaram: {}'.format(MAX_CARS))

    print('Tempo de espera (fila esquerda):')
    print('Máximo: {}'.format(max(waiting_left)))
    print('Mínimo: {}'.format(min(waiting_left)))
    print('Média: {}'.format(np.mean(waiting_left)))

    print('\nTempo de espera (fila direita):')
    print('Máximo: {}'.format(max(waiting_right)))
    print('Mínimo: {}'.format(min(waiting_right)))
    print('Média: {}'.format(np.mean(waiting_right)))

    print('\nTempo de utilização total da ponte: {}'.format(timing))

    S = '\nTempo total de funcionamento do programa: {}'.format(program_time)
    print(S)


# Código que será executado
def main():
    program_time = time.time()
    global program_end
    cv_bridge = Condition()
    cv_queue = Condition()

    time_calculator = Thread(target=thread_time_calculator, args=(cv_bridge, ))
    time_calculator.start()

    remove = Thread(target=thread_remove_cars, args=(cv_bridge, ))
    remove.start()

    bridge = Thread(target=thread_bridge, args=(cv_bridge, cv_queue))
    bridge.start()

    queue = Thread(target=thread_queue, args=(cv_queue, ))
    queue.start()

    bridge.join()
    program_end = True
    with(cv_bridge):
        cv_bridge.notify_all()
    time_calculator.join()

    current_time = time.time()
    program_time = current_time - program_time
    results(program_time)


if(__name__ == '__main__'):
    main()
