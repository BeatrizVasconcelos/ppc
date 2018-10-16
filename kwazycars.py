# Imports
from threading import Thread
from threading import Condition
from random import randint
from random import choice
import time
from collections import deque
import numpy as np
import classes

# Variáveis globais
# Fila de veículos que vão para a direção esquerda
left = deque([])
# Fila de veículos que vão para a direção direita
right = deque([])
# Ponte
bridge = classes.Bridge()
# Tempos de espera de veículos que vão para a esquerda
waiting_left = []
# Tempos de espera de veículos que vão para a direita
waiting_right = []
# Tempo de uso da ponte
timing = 0
# Flag para sinalizar que o programa acabou
program_end = False
# Constantes de limite de carros e caminhões
MAX_CARS = 100
MAX_TRUCKS = 6
# Contador de veículos
total_vehicles = 0


# Função que escolhe veiculo
def choose_vehicle():
    # Veículo, tempo e sentido
    vehicle = None
    timing = None
    direction = None
    # Verifica se há veículo(s) na ponte
    if(len(bridge.vehicles) > 0):
        # Se a direção da ponte for direita e houver veículos na fila direita,
        # o veículo é retirado da fila
        if(bridge.direction == 'right' and len(right) > 0):
            vehicle, timing = right.popleft()
            direction = 'right'
        # Se a direção da ponte for esquerda e houver veículos na fila
        # esquerda, o veículo é retirado da fila
        elif(bridge.direction == 'left' and len(left) > 0):
            vehicle, timing = left.popleft()
            direction = 'left'
    # Caso não hajam veículos na ponte:
    else:
        available_queues = []
        # Se houver veículo(s) na fila esquerda, adiciona
        # a fila esquerda à lista de filas disponíveis
        if(len(left) > 0):
            available_queues.append('left')
        # Se houver veículo(s) na fila direita, adiciona
        # a fila direita à lista de filas disponíveis
        elif(len(right) > 0):
            available_queues.append('right')
        # Escolhe aleatoriamente uma direção entre as direções
        # disponíveis
        direction = choice(available_queues)
        # Se a direção escolhida for direita, tira um veículo da fila direita
        if(direction == 'right'):
            vehicle, timing = right.popleft()
        # Se a direção escolhida for esquerda, tira um veículo da fila esquerda
        else:
            vehicle, timing = left.popleft()
    # Retorna um veículo, seu tempo de chegada na fila e sua direção
    return vehicle, timing, direction


# Thread da ponte
def thread_bridge(cv_bridge, cv_queue):
    # Variáveis globais importadas
    global total_vehicles
    global bridge

    while(True):
        # Flag para sinalizar se o veículo é um caminhão ou não
        is_truck = False
        # Enquanto não houver veículo(s) em nenhuma das filas, a thread espera
        with(cv_queue):
            while(len(right) == 0 and len(left) == 0):
                cv_queue.wait()
        # Escolhe um veículo
        vehicle, timing, direction = choose_vehicle()
        # Se não houver nenhum veículo que possa ser colocado na ponte, retorna
        # para o loop
        if(not vehicle):
            continue
        # Seta a direção da ponte para a mesma do carro que foi escolhido
        bridge.set_direction(direction)

        # Imprime a direção da ponte
        if(bridge.direction == 'right'):
            print('Sentido da ponte: {}'.format(bridge.direction))
        else:
            print('Sentido da ponte: {}'.format(bridge.direction))

        # Se o veículo for um caminhão, espera a ponte esvaziar
        if(isinstance(vehicle, classes.Truck)):
            is_truck = True
            # Enquanto houver veículo(s) na ponte, a thread notifica as outras
            # e dorme
            with(cv_bridge):
                while(len(bridge.vehicles) > 0):
                    cv_bridge.notify_all()
                    cv_bridge.wait()
                    print('Ponte esvaziou.')

        # Calcula o tempo de espera do veículo (tempo atual - tempo de chegada)
        waiting_time = time.time() - timing

        # Se a direção da ponte for direita, armazena o tempo de espera da fila
        # direita
        if(bridge.direction == 'right'):
            waiting_right.append(waiting_time)
        # Se a direção da ponte for esquerda, armazena o tempo de espera da
        # fila esquerda
        else:
            waiting_left.append(waiting_time)

        # Tupla que guarda o veículo e seu tempo de chegada
        tup = (vehicle, time.time())
        # Veículo é inserido na ponte
        bridge.vehicles.append(tup)
        print('Veículo entrou na ponte')

        # Thread notifica as outras que há veículo(s) na ponte
        with(cv_bridge):
            cv_bridge.notify_all()

        # Incrementa o número total de veículos
        total_vehicles += 1
        print('Veículos na ponte: {}'.format(len(bridge.vehicles)))
        print('Total de veículos: {}'.format(total_vehicles))

        # Se o veículo atual for um caminhão, espera a ponte esvaziar
        # para que outro veículo seja inserido
        if(is_truck):
            with(cv_bridge):
                while(len(bridge.vehicles) > 0):
                    cv_bridge.notify_all()
                    cv_bridge.wait()
        # Caso seja um carro, espera 2 segundos para que outro veículo
        # entre na ponte
        else:
            time.sleep(2)

        # Se o total de veículos atingir 106 (100 carros e 6 caminhões),
        # a thread é encerrada
        if(total_vehicles >= MAX_CARS + MAX_TRUCKS):
            print('Thread bridge encerrou')
            break


# Thread que gera carros
def thread_queue(cv_queue):
    # 0 = carro esquerda, 1 = carro direita
    # 2 = caminhão esquerda, 3 = caminhão direita
    combinations = [0, 1, 2, 3]
    # Carros que vão para direita
    cars_right = 0
    # Carros que vão para esquerda
    cars_left = 0
    # Caminhões que vão para direita
    trucks_right = 0
    # Caminhões que vão para esquerda
    trucks_left = 0
    while(True):
        # Se não houverem combinações, a thread é encerrada
        if(len(combinations) == 0):
            break
        # Gera uma combinação de veículo e sentido
        combination = choice(combinations)
        # Se a combinação for 0, insere um carro na esquerda
        if(combination == 0):
            # Tupla para guardar o veículo e seu tempo de chegada
            tup = (classes.Car(), time.time())
            left.append(tup)
            cars_left += 1
            print('Carro inserido na fila esquerda')
            # Se o número de carros que foram para a direção esquerda
            # atingir 50, a combinação 0 é removida
            if(cars_left == 50):
                combinations.remove(0)
        # Se a combinação for 1, insere um carro na direita
        elif(combination == 1):
            tup = (classes.Car(), time.time())
            right.append(tup)
            cars_right += 1
            print('Carro inserido na fila direita')
            # Se o número de carros que foram para a direção direita
            # atingir 50, a combinação 1 é removida
            if(cars_right == 50):
                combinations.remove(1)
        # Se a combinação for 2, insere um caminhão na esquerda
        elif(combination == 2):
            tup = (classes.Truck(), time.time())
            left.append(tup)
            trucks_left += 1
            print('Caminhão inserido na fila esquerda')
            # Se o número de caminhões que foram para a direção esquerda
            # atingir 3, a combinação 2 é removida
            if(trucks_left == 3):
                combinations.remove(2)
        # Se a combinação for 2, insere um caminhão na direita
        elif(combination == 3):
            tup = (classes.Truck(), time.time())
            right.append(tup)
            trucks_right += 1
            print('Caminhão inserido na fila direita')
            # Se o número de caminhões que foram para a direção direita
            # atingir 3, a combinação 3 é removida
            if(trucks_right == 3):
                combinations.remove(3)

        # Notifica todas as threads após inserir um veículo em uma das filas
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

        # Tempo de travessia de cada veículo
        crossing_time = bridge.vehicles[0][0].time_to_pass

        # Espera o carro atravessar a ponte
        while((time.time() - bridge.vehicles[0][1]) < crossing_time):
            pass
        # Retira o veículo da ponte
        bridge.vehicles.popleft()
        # Notifica as outras threads
        with(cv_bridge):
            cv_bridge.notify_all()
        # Incrementa os veículos removidos
        removed_vehicles += 1
        print('Veículo removido da direção {}\n\n'.format(bridge.direction))
        # Se o número de veículos removidos for igual a 106,
        # a thread é encerrada
        if(removed_vehicles >= MAX_CARS + MAX_TRUCKS):
            print('Thread remove vehicles encerrou')
            break


# Thread que calcula o tempo de utilização da ponte
def thread_time_calculator(cv_bridge):
    # Variável importada
    global timing
    while(True):
        # Enquanto não houverem veículos na ponte e o programa
        # não é encerrado, a thread espera
        while(len(bridge.vehicles) == 0 and not program_end):
            with(cv_bridge):
                cv_bridge.wait()

        # Tempo em que a ponte começou a ser usada
        init = time.time()

        # Enquanto houverem veículos na ponte e o programa
        # não é encerrado, a thread espera
        while(len(bridge.vehicles) >= 1 and not program_end):
            with(cv_bridge):
                cv_bridge.wait()

        # Tempo de utilização da ponte
        using_time = time.time() - init
        # Tempo total de utilização da ponte
        timing += using_time

        # Caso o programa seja encerrado, a thread para
        if(program_end):
            print('Thread time calculator encerrou')
            break


# Função que exibe os resultados
def results(program_time):
    print('Número total de carros que atravessaram: {}'.format(MAX_CARS))
    print('Número total de caminhões que atravessaram: {}'.format(MAX_TRUCKS))

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
    # Tempo inicial de execução do programa
    program_time = time.time()
    # Variável "importada"
    global program_end
    # Variáveis de condição
    cv_bridge = Condition()
    cv_queue = Condition()

    # Inicia thread time_calculator
    time_calculator = Thread(target=thread_time_calculator, args=(cv_bridge, ))
    time_calculator.start()

    # Inicia thread remove
    remove = Thread(target=thread_remove_vehicles, args=(cv_bridge, ))
    remove.start()

    # Inicia thread bridge
    bridge = Thread(target=thread_bridge, args=(cv_bridge, cv_queue))
    bridge.start()

    # Inicia thread queue
    queue = Thread(target=thread_queue, args=(cv_queue, ))
    queue.start()

    # Espera thread bridge terminar de executar
    bridge.join()
    # Espera thread remove terminar de executar
    remove.join()

    # Altera a flag para notificar outras threads
    program_end = True

    # Notifica as threads
    with(cv_bridge):
        cv_bridge.notify_all()

    # Espera a thread time_calculator terminar de executar
    time_calculator.join()

    # Tempo atual
    current_time = time.time()

    # Tempo total de execução do programa
    program_time = current_time - program_time

    # Chama a função results
    results(program_time)


# Caso o arquivo esteja sendo executado sem
# ser importado (python3 kwazycars.py),
# chama  a função main
if(__name__ == '__main__'):
    main()
