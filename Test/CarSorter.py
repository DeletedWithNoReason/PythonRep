from models import Car, Bus, Bicycle, ElectricCar

if __name__ == "__main__":
    transports = [
        Car("Легковик", 100, 4),
        Bus("Автобус", 80, 30, passengers=25),
        Bicycle("Велосипед", 25, 1),
        ElectricCar("Тесла", 120, 5)
    ]

    distance = 100.0
    for t in transports:
        print(t.info(distance))