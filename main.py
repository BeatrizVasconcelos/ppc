"""
Classe para implementar um objeto veículo:
Utilizada para implementar herança, possui um
atributo para o tempo de travessia.
"""


class Vehicle:
    def __init__(self, time):
        self.time_to_pass = time


class Car(Vehicle):
    def __init__(self):
        super().__init__(10)


class Bridge:
    def __init__(self):
        self.vehicles = []
        self.direction = 'left'

    def change_direction(self):
        if(self.direction == 'left'):
            self.direction == 'right'
        else:
            self.direction == 'left'


def main():
    bridge = Bridge()
    print(bridge)


if(__name__ == '__main__'):
    main()
