from TempMedicineSorter.models1 import Antibiotic, Vitamin, Vaccine

def print_medicines_info(medicines: list):
    for med in medicines:
        print(med.info())

if __name__ == "__main__":
    items = [
        Antibiotic("Амоксицилін", 2, 120.0),
        Vitamin("Вітамін C", 5, 45.0),
        Vaccine("Вакцина X", 10, 300.0)
    ]

    print_medicines_info(items)