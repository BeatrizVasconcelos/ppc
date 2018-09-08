# Classe Vehicle
class Vehicle:
    def __init__(self, time):
        self.time_to_pass = time


# Classe Car que herda de Vehicle
class Car(Vehicle):
    def __init__(self):
        super().__init__(10)


# Classe Bridge
class Bridge:
    def __init__(self):
        self.vehicles = []
        self.direction = 'left'

    def change_direction(self):
        if(self.direction == 'left'):
            self.direction == 'right'
        else:
            self.direction == 'left'
