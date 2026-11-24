from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


NEW_CONDITION_FACTOR = 1.0
USED_CONDITION_FACTOR = 0.7
BROKEN_CONDITION_FACTOR = 0.2


class Condition(str, Enum):
    NEW = "новий"
    USED = "уживаний"
    BROKEN = "зламаний"

    @property
    def factor(self) -> float:
        mapping = {
            Condition.NEW: NEW_CONDITION_FACTOR,
            Condition.USED: USED_CONDITION_FACTOR,
            Condition.BROKEN: BROKEN_CONDITION_FACTOR,
        }
        return mapping[self]

    @classmethod
    def from_raw(cls, raw: str) -> "Condition":
        normalized = raw.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        # Для сумісності зі старою поведінкою ("else: повна ціна")
        return cls.NEW


@dataclass(order=True)
class Item:
    # Порядок полів визначає order=True: спочатку category, потім value (від меншого до більшого)
    category: str
    value: float
    name: str = field(compare=False)
    quantity: int = field(compare=False)
    condition: Condition = field(compare=False, default=Condition.NEW)
    location: str = field(compare=False, default="")
    added_at: datetime = field(compare=False, repr=False, default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.name = str(self.name).strip()
        self.category = str(self.category).strip()
        self.location = str(self.location).strip()
        self.quantity = int(self.quantity)
        self.value = float(self.value)
        if not isinstance(self.condition, Condition):
            self.condition = Condition.from_raw(str(self.condition))

        if not self.name:
            raise ValueError("Назва предмета не може бути порожньою.")
        if not self.category:
            raise ValueError("Категорія предмета не може бути порожньою.")
        if self.quantity < 0:
            raise ValueError("Кількість не може бути від'ємною.")
        if self.value < 0:
            raise ValueError("Ціна не може бути від'ємною.")

    def total_value(self) -> float:
        return self.quantity * self.value * self.condition.factor

    def __str__(self) -> str:
        cond_text = self.condition.value if isinstance(self.condition, Condition) else str(self.condition)
        return (
            f"[{self.category}] {self.name} ({self.quantity} шт.) - "
            f"{self.value} грн/шт, стан: {cond_text}"
        )


def _format_legacy_number(num: float) -> str:
    return str(round(num, 2))


@dataclass
class Inventory:
    items: list[Item] = field(default_factory=list)

    def add_item(self, item: Item) -> None:
        if any(existing.name == item.name for existing in self.items):
            raise ValueError(f"Предмет із назвою '{item.name}' уже є на складі.")
        self.items.append(item)

    def remove_item(self, name: str) -> bool:
        for idx, existing in enumerate(self.items):
            if existing.name == name:
                del self.items[idx]
                return True
        return False

    def find_by_category(self, category: str) -> list[Item]:
        target = category.strip().lower()
        return [item for item in self.items if item.category.lower() == target]

    def total_inventory_value(self) -> float:
        return sum(item.total_value() for item in self.items)

    def filter_items(self, **criteria: Any) -> list[Item]:
        """
        Універсальна фільтрація за будь-якими полями Item.
        Підтримує як точні/чутливі до регістру значення, так і callable-предикати.
        """
        result: list[Item] = []
        for item in self.items:
            matched = True
            for attr, expected in criteria.items():
                if not hasattr(item, attr):
                    raise AttributeError(f"У Item відсутнє поле '{attr}'.")
                actual = getattr(item, attr)
                if callable(expected):
                    if not expected(actual):
                        matched = False
                        break
                else:
                    if isinstance(actual, str) and isinstance(expected, str):
                        if actual.lower() != expected.strip().lower():
                            matched = False
                            break
                    elif actual != expected:
                        matched = False
                        break
            if matched:
                result.append(item)
        return result

    def sorted_items(self, key: str = "default", reverse: bool = False) -> list[Item]:
        """
        Сортування предметів.
        За замовчуванням ("default") використовує природний порядок Item (category, потім value).
        """
        if key == "default":
            return sorted(self.items, reverse=reverse)
        return sorted(self.items, key=lambda item: getattr(item, key), reverse=reverse)

    def export_summary(self) -> dict[str, int]:
        """Повертає кількість предметів (кількість записів/одиниць? — кількість позицій/предметів по категоріях)."""
        summary: dict[str, int] = {}
        for item in self.items:
            summary[item.category] = summary.get(item.category, 0) + 1
        return summary

    def save_to_csv(self, filepath: str | Path) -> None:
        path = Path(filepath)
        lines = [
            f"{item.name};{item.category};{item.quantity};{item.value};{item.condition.value};{item.location}"
            for item in self.items
        ]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    @classmethod
    def load_from_csv(cls, filepath: str | Path) -> "Inventory":
        path = Path(filepath)
        inv = cls()
        with path.open("r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split(";")
                if len(parts) < 5:
                    raise ValueError(f"Некоректний рядок у CSV: '{line}'")
                name, category, qty_raw, val_raw, cond_raw = parts[:5]
                location = parts[5] if len(parts) >= 6 else ""
                item = Item(
                    name=name,
                    category=category,
                    quantity=int(qty_raw.strip()),
                    value=float(val_raw.strip()),
                    condition=Condition.from_raw(cond_raw),
                    location=location,
                )
                inv.add_item(item)
        return inv


def load_legacy_csv(filepath: str | Path) -> Inventory:
    """Завантажує дані з CSV формату старого блокнота, повертаючи новий Inventory."""
    return Inventory.load_from_csv(filepath)


def render_legacy_report(inventory: Inventory) -> str:
    """Відтворює вивід старого звіту без змін."""
    total_val = inventory.total_inventory_value()
    lines = [f"Барахла: {len(inventory.items)}"]
    for item in sorted(inventory.items, key=lambda it: it.location):
        item_val = item.total_value()
        lines.append(
            f"{item.location} | {item.name} | {item.quantity} шт | {_format_legacy_number(item_val)}"
        )
    lines.append(f"Разом: {_format_legacy_number(total_val)}")
    return "\n".join(lines) + "\n"