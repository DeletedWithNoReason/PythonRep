from abc import ABC, abstractmethod

class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        self.name = name
        self.speed = speed
        self.capacity = capacity

    def move(self, distance: float) -> float:
        return distance / self.speed

    @abstractmethod
    def fuel_consumption(self, distance: float) -> float:
        pass

    def calculate_cost(self, distance: float, price_per_unit: float) -> float:
        return self.fuel_consumption(distance) * price_per_unit

    def info(self, distance: float = 100.0) -> str:
        time_taken = self.move(distance)
        fuel = self.fuel_consumption(distance)
        return f"{self.name} | Час на {distance} км: {time_taken:.2f} год | Витрати пального: {fuel} л"


class Car(Transport):
    def fuel_consumption(self, distance: float) -> float:
        return distance * 0.07


class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int):
        super().__init__(name, speed, capacity)
        self.passengers = passengers

    def fuel_consumption(self, distance: float) -> float:
        if self.passengers > self.capacity:
            raise ValueError("Перевантажено!")
        return distance * 0.15


class Bicycle(Transport):
    def __init__(self, name: str, speed: int, capacity: int):
        actual_speed = min(speed, 20)
        super().__init__(name, actual_speed, capacity)

    def fuel_consumption(self, distance: float) -> float:
        return 0.0


class ElectricCar(Car):
    def battery_usage(self, distance: float) -> float:
        return distance * 0.2

    def fuel_consumption(self, distance: float) -> float:
        return 0.0