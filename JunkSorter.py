from abc import ABC, abstractmethod


class JunkItem:

  def __init__(self, name: str, quantity: int, value: float):
    self.name = name
    self.quantity = quantity
    self.value = value

  def __repr__(self) -> str:
    return (
        f"JunkItem(name='{self.name}', quantity={self.quantity},"
        f" value={self.value})"
    )


class StorageBackend(ABC):

  @abstractmethod
  def save(self, items: list[JunkItem]) -> None:
    pass

  @abstractmethod
  def load(self) -> list[JunkItem]:
    pass


class JunkStorage(StorageBackend):

  def __init__(self, filename: str):
    self.filename = filename

  def serialize(self, items: list[JunkItem], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
      for item in items:
        value_str = str(item.value).replace(".", ",")
        line = f"{item.name}|{item.quantity}|{value_str}\n"
        f.write(line)

  def parse(self, filename: str) -> list[JunkItem]:
    items = []
    try:
      with open(filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
          line = line.strip()
          if not line:
            continue

          parts = line.split("|")
          if len(parts) != 3:
            print(
                f"[Попередження] Рядок {line_num} пропущено: невірний формат"
                f" (очікувалося 3 поля, отримано {len(parts)})."
            )
            continue

          name_str, qty_str, val_str = parts

          try:
            quantity = int(qty_str)
            value = float(val_str.replace(",", "."))
          except ValueError:
            print(
                f"[Попередження] Рядок {line_num} пропущено: помилка конвертації"
                f" типів даних (qty={qty_str}, val={val_str})."
            )
            continue

          items.append(JunkItem(name_str, quantity, value))
    except FileNotFoundError:
      print(
          f"[Інформація] Файл '{filename}' не знайдено. Повертається порожній"
          " список."
      )

    return items

  def save(self, items: list[JunkItem]) -> None:
    self.serialize(items, self.filename)

  def load(self) -> list[JunkItem]:
    return self.parse(self.filename)

class Warehouse:

  def __init__(self, storage: StorageBackend):
    self.storage = storage
    self.items: list[JunkItem] = []

  def add_item(self, item: JunkItem) -> None:
    self.items.append(item)

  def save_inventory(self) -> None:
    self.storage.save(self.items)

  def load_inventory(self) -> None:
    self.items = self.storage.load()

  def find_item(self, name: str) -> list[JunkItem]:
    return [i for i in self.items if name.lower() in i.name.lower()]


if __name__ == "__main__":
  filename = "warehouse_stock.csv"

  storage = JunkStorage(filename)
  warehouse = Warehouse(storage)

  print("=== КРОК 3: Створення предметів та запис у файл ===")
  warehouse.add_item(JunkItem("Бляшанка", 5, 2.5))
  warehouse.add_item(JunkItem("Стара плата", 3, 7.8))
  warehouse.add_item(JunkItem("Купка дротів", 10, 1.2))

  warehouse.save_inventory()
  print("Дані успішно збережено у файл.")

  print("\n=== КРОК 4: Читання з файлу та перевірка збереження значень ===")
  new_warehouse = Warehouse(storage)
  new_warehouse.load_inventory()

  for item in new_warehouse.items:
    print(
        f"Зчитано -> Назва: {item.name}, Кількість: {item.quantity}"
        f" ({type(item.quantity)}), Вартість: {item.value}"
        f" ({type(item.value)})"
    )

  print("\n=== КРОК 5: Перевірка на зіпсовані рядки ===")
  with open(filename, "a", encoding="utf-8") as f:
    f.write("Битий рядок без роздільників\n")
    f.write("Радіодеталь|не_число|5,0\n")
    f.write("Труба|15|не_float_ціна\n")

  test_warehouse = Warehouse(storage)
  test_warehouse.load_inventory()

  print("Успішно завантажені лише валідні об'єкти:")
  for item in test_warehouse.items:
    print(f" - {item.name}")