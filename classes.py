from collections import deque


# Classe Vehicle
class Vehicle:
    def __init__(self, time):
        self.time_to_pass = time


# Classe Car que herda de Vehicle
class Car(Vehicle):
    def __init__(self):
        super().__init__(10)


# Classe Truck que herda de Vehicle
class Truck(Vehicle):
    def __init__(self):
        super().__init__(20)


# Classe Bridge
class Bridge:
    def __init__(self):
        self.vehicles = deque([])
        self.direction = 'left'

    def change_direction(self):
        if(self.direction == 'left'):
            self.direction = 'right'
        else:
            self.direction = 'left'

    def set_direction(self, direction):
        self.direction = direction
