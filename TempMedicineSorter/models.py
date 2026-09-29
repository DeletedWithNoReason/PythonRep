from abc import ABC, abstractmethod

class Medicine(ABC):
    def __init__(self, name: str, quantity: int, price: float):
        if type(name) is not str or type(quantity) is not int or type(price) not in (int, float) or type(price) is bool:
            raise TypeError("Некоректні типи даних у конструкторі")

        self.name = name
        self.quantity = quantity
        self.price = price

    @abstractmethod
    def requires_prescription(self) -> bool:
        pass

    @abstractmethod
    def storage_requirements(self) -> str:
        pass

    def total_price(self) -> float:
        return float(self.quantity * self.price)

    def info(self) -> str:
        rx = "Так" if self.requires_prescription() else "Ні"
        return f"{self.name} | К-сть: {self.quantity} | Ціна: {self.total_price()} грн | Рецепт: {rx} | Умови: {self.storage_requirements()}"

class Antibiotic(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "8–15°C, темне місце"

class Vitamin(Medicine):
    def requires_prescription(self) -> bool:
        return False

    def storage_requirements(self) -> str:
        return "15–25°C, сухо"

class Vaccine(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "2–8°C, холодильник"

    def total_price(self) -> float:
        base_price = super().total_price()
        return base_price * 1.1