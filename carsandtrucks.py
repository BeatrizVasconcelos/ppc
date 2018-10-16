from threading import Thread
from threading import Condition
from random import randint
from random import choice
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
reset = False
MAX_CARS = 100
MAX_TRUCKS = 6
total_vehicles = 0


# Função da Thread Bridge
def thread_bridge(cv_bridge, cv_queue):
    num_vehicles = 0
    global total_vehicles
    global bridge
    global reset

    while(True):
        is_truck = False
        with(cv_queue):
            while(bridge.direction == 'right' and len(right) == 0):
                print('Ponte esperando veículo na fila direita')
                cv_queue.wait()
            while(bridge.direction == 'left' and len(left) == 0):
                print('Ponte esperando veículo na fila esquerda')
                cv_queue.wait()

        if(reset):
            reset = False
            num_vehicles = 0
            continue

        if(bridge.direction == 'right'):
            print('Sentido da ponte: {}'.format(bridge.direction))
            vehicle, start_time = right.popleft()
        else:
            print('Sentido da ponte: {}'.format(bridge.direction))
            vehicle, start_time = left.popleft()

        if(isinstance(vehicle, classes.Truck)):
            is_truck = True
            with(cv_bridge):
                while(len(bridge.vehicles) > 0):
                    cv_bridge.notify_all()
                    cv_bridge.wait()
                    print('Ponte esvaziou.')

        waiting_time = time.time() - start_time

        if(bridge.direction == 'right'):
            waiting_right.append(waiting_time)
        else:
            waiting_left.append(waiting_time)

        tup = (vehicle, time.time())
        bridge.vehicles.append(tup)
        print('Veículo entrou na ponte')

        with(cv_bridge):
            cv_bridge.notify_all()

        num_vehicles += 1
        total_vehicles += 1
        s = 'Veículos atravessados na mesma direção: {}'.format(num_vehicles)
        print(s)
        print('Veículos na ponte: {}'.format(len(bridge.vehicles)))
        print('Total de veículos: {}'.format(total_vehicles))
        s = 'Veículos atravessados na mesma direção: {}'.format(num_vehicles)
        print(s)

        if(is_truck):
            with(cv_bridge):
                while(len(bridge.vehicles) > 0):
                    cv_bridge.notify_all()
                    cv_bridge.wait()
        else:
            time.sleep(2)

        if(num_vehicles >= 5):
            with(cv_bridge):
                while(len(bridge.vehicles) > 0):
                    cv_bridge.notify_all()
                    cv_bridge.wait()
            bridge.change_direction()
            num_vehicles = 0

        if(total_vehicles >= MAX_CARS + MAX_TRUCKS):
            print('Thread bridge encerrou')
            break


def thread_timeout(cv_bridge, cv_queue):
    global reset
    while(True):
        with(cv_bridge):
            while(len(bridge.vehicles) > 0 and not program_end):
                cv_bridge.wait()

        if(total_vehicles <= 100):
            continue

        if(program_end):
            print('Thread timeout encerrou.')
            break

        start_time = time.time()
        while(not timeout_condition(time.time() - start_time)):
            pass

        bridge.change_direction()
        reset = True

        with(cv_queue):
            cv_queue.notify_all()

        if(program_end):
            break


def timeout_condition(timing):
    flag = False
    if(bridge.direction == 'right' and len(left) > 0 and len(right) == 0):
        flag = True
    elif(bridge.direction == 'left' and len(right) > 0 and len(left) == 0):
        flag = True
    return len(bridge.vehicles) == 0 and flag and timing >= 15


# Função que gera carros
def thread_queue(cv_queue):
    # 0 = carro esquerda, 1 = carro direita
    # 2 = caminhão esquerda, 3 = caminhão direita
    combinations = [0, 1, 2, 3]
    cars_right = 0
    cars_left = 0
    trucks_right = 0
    trucks_left = 0
    while(True):
        if(len(combinations) == 0):
            break
        # Gera uma combinação de veículo e sentido
        combination = choice(combinations)

        if(combination == 0):
            # Tupla para guardar o veículo e seu tempo de chegada
            tup = (classes.Car(), time.time())
            left.append(tup)
            cars_left += 1
            print('Carro inserido na fila esquerda')
            if(cars_left == 50):
                combinations.remove(0)
        elif(combination == 1):
            tup = (classes.Car(), time.time())
            right.append(tup)
            cars_right += 1
            print('Carro inserido na fila direita')
            if(cars_right == 50):
                combinations.remove(1)
        elif(combination == 2):
            tup = (classes.Truck(), time.time())
            left.append(tup)
            trucks_left += 1
            print('Caminhão inserido na fila esquerda')
            if(trucks_left == 3):
                combinations.remove(2)
        elif(combination == 3):
            tup = (classes.Truck(), time.time())
            right.append(tup)
            trucks_right += 1
            print('Caminhão inserido na fila direita')
            if(trucks_right == 3):
                combinations.remove(3)

        # Notifica todas as threads após inserir um carro em uma das filas
        with(cv_queue):
            cv_queue.notify_all()

        # Gera um tempo de chegada aleatório e espera esse tempo
        waiting_time = randint(2, 6)
        time.sleep(waiting_time)
    print('Thread queue encerrou')


# Thread que retira os veículos da ponte, após passados 10
# segundos de travessia
def thread_remove_vehicles(cv_bridge):
    removed_vehicles = 0
    while(True):
        # Se não houver veículos, a thread notifica as outras
        # e depois, dorme
        with(cv_bridge):
            while(len(bridge.vehicles) == 0):
                print('Ponte vazia')
                time.sleep(3)
                cv_bridge.notify_all()
                cv_bridge.wait()
        crossing_time = bridge.vehicles[0][0].time_to_pass
        while((time.time() - bridge.vehicles[0][1]) < crossing_time):
            pass
        bridge.vehicles.popleft()
        with(cv_bridge):
            cv_bridge.notify_all()
        removed_vehicles += 1
        print('Veículo removido da direção {}\n\n'.format(bridge.direction))
        if(removed_vehicles >= MAX_CARS + MAX_TRUCKS):
            print('Thread remove vehicles encerrou')
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

    remove = Thread(target=thread_remove_vehicles, args=(cv_bridge, ))
    remove.start()

    bridge = Thread(target=thread_bridge, args=(cv_bridge, cv_queue))
    bridge.start()

    queue = Thread(target=thread_queue, args=(cv_queue, ))
    queue.start()

    timeout = Thread(target=thread_timeout, args=(cv_bridge, cv_queue))
    timeout.start()

    bridge.join()
    remove.join()
    program_end = True
    with(cv_bridge):
        cv_bridge.notify_all()
    time_calculator.join()
    timeout.join()

    current_time = time.time()
    program_time = current_time - program_time
    results(program_time)


if(__name__ == '__main__'):
    main()
