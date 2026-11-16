import csv
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

@dataclass
class Product:
    id: str
    name: str
    category: str
    quantity: int
    price: float
    location: str
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class CsvStorage:
    HEADERS = ["id", "name", "category", "quantity", "price", "location", "created_at"]

    def load(self, filepath: str) -> list[Product]:
        if not os.path.exists(filepath):
            raise FileNotFoundError("Файл не знайдено.")

        products = []
        seen_ids = set()

        with open(filepath, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or set(self.HEADERS) != set(reader.fieldnames):
                raise ValueError(f"Невірний формат заголовків CSV. Очікуються: {', '.join(self.HEADERS)}")

            for line_num, row in enumerate(reader, start=2):
                try:
                    p_id = (row["id"] or "").strip()
                    name = (row["name"] or "").strip()
                    category = (row["category"] or "").strip()
                    location = (row["location"] or "").strip()
                    created_at = (row["created_at"] or "").strip() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if not p_id or not name or not category:
                        raise ValueError("Порожні обов'язкові поля (id, name або category).")
                    if p_id in seen_ids:
                        raise ValueError(f"Дублікат ID '{p_id}'.")

                    qty = int(row["quantity"])
                    price = float(str(row["price"]).replace(",", "."))

                    if qty < 0 or price < 0:
                        raise ValueError("Кількість або ціна менше нуля.")

                    seen_ids.add(p_id)
                    products.append(Product(p_id, name, category, qty, price, location, created_at))
                except Exception as e:
                    raise ValueError(f"Помилка у рядку {line_num}: {e}")

        return products

    def save(self, filepath: str, products: list[Product]) -> None:
        with open(filepath, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            for p in products:
                writer.writerow({
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "quantity": p.quantity,
                    "price": f"{p.price:.2f}",
                    "location": p.location,
                    "created_at": p.created_at,
                })

class InventoryApp:
    def __init__(self, root: tk.Tk, storage: CsvStorage):
        self.root = root
        self.storage = storage
        self.root.title("Облік товарів на складі")
        self.root.geometry("1050x560")
        self.root.minsize(850, 480)

        self.products: list[Product] = []
        self.current_filepath: str | None = None
        self.selected_id: str | None = None
        self.sort_reverse: dict[str, bool] = {}

        self.entries: dict[str, tk.Entry] = {}

        self._setup_menu()
        self._setup_ui()
        self._seed_demo_data()
        self.refresh_table()
        self.set_status("Готово до роботи.")

    def _setup_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Відкрити...", command=self.on_open, accelerator="Ctrl+O")
        file_menu.add_command(label="Зберегти", command=self.on_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Зберегти як...", command=self.on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu=menubar)

        self.root.bind("<Control-o>", lambda e: self.on_open())
        self.root.bind("<Control-s>", lambda e: self.on_save())

    def _setup_ui(self):
        search_frame = ttk.Frame(self.root, padding=(10, 10, 10, 5))
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Пошук (назва або категорія):").pack(side=tk.LEFT, padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_table())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(search_frame, text="Скинути пошук", command=lambda: self.search_var.set("")).pack(side=tk.LEFT, padx=(8, 0))

        main_frame = ttk.Frame(self.root, padding=(10, 5, 10, 5))
        main_frame.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        columns = ("id", "name", "category", "quantity", "price", "location", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headers_map = {
            "id": ("ID", 90),
            "name": ("Назва", 180),
            "category": ("Категорія", 120),
            "quantity": ("Кількість", 80),
            "price": ("Ціна", 85),
            "location": ("Склад / Полиця", 110),
            "created_at": ("Створено", 135),
        }

        for col, (text, width) in headers_map.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
            anchor = tk.E if col in ("quantity", "price") else tk.W
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        form_frame = ttk.LabelFrame(main_frame, text="Картка товару", padding=12)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y)

        fields_spec = [
            ("id", "ID (порожньо = авто):"),
            ("name", "Назва *:"),
            ("category", "Категорія *:"),
            ("quantity", "Кількість (ціле ≥ 0) *:"),
            ("price", "Ціна (≥ 0) *:"),
            ("location", "Склад / Полиця:"),
        ]

        for row_idx, (field_key, label_text) in enumerate(fields_spec):
            ttk.Label(form_frame, text=label_text).grid(row=row_idx * 2, column=0, sticky=tk.W, pady=(2, 0))
            entry = tk.Entry(form_frame, width=28, font=("TkDefaultFont", 10))
            entry.grid(row=row_idx * 2 + 1, column=0, sticky=tk.EW, pady=(0, 8))
            self.entries[field_key] = entry

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields_spec) * 2, column=0, pady=(10, 0), sticky=tk.EW)

        ttk.Button(btn_frame, text="Додати", command=self.on_add).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="Оновити", command=self.on_update).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="Видалити", command=self.on_delete).pack(fill=tk.X, pady=3)
        ttk.Separator(btn_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Button(btn_frame, text="Очистити форму", command=self.clear_form).pack(fill=tk.X, pady=3)

        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(10, 4))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _seed_demo_data(self):
        self.products = [
            Product("101", "Кабель HDMI 2.0", "Кабелі", 25, 180.50, "Стелаж А-1"),
            Product("102", "Миша дротова USB", "Периферія", 14, 320.00, "Полиця Б-3"),
            Product("103", "Термопаста 4г", "Витратні", 8, 215.75, "Сейф-2"),
        ]

    def set_status(self, message: str, is_error: bool = False):
        prefix = "⚠️ ПОМИЛКА: " if is_error else "ℹ️ "
        self.status_var.set(prefix + message)

    def reset_highlights(self):
        for entry in self.entries.values():
            entry.config(bg="white")

    def highlight_error(self, field_key: str, message: str):
        self.reset_highlights()
        if field_key in self.entries:
            self.entries[field_key].config(bg="#ffcccc")
            self.entries[field_key].focus_set()
        self.set_status(message, is_error=True)

    def clear_form(self):
        self.reset_highlights()
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.selected_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.set_status("Форму очищено.")

    def _validate_and_build(self, is_update: bool = False) -> Product | None:
        self.reset_highlights()

        raw_id = self.entries["id"].get().strip()
        name = self.entries["name"].get().strip()
        category = self.entries["category"].get().strip()
        raw_qty = self.entries["quantity"].get().strip()
        raw_price = self.entries["price"].get().strip().replace(",", ".")
        location = self.entries["location"].get().strip()

        if not name:
            self.highlight_error("name", "Поле 'Назва' не може бути порожнім.")
            return None
        if not category:
            self.highlight_error("category", "Поле 'Категорія' не може бути порожнім.")
            return None

        try:
            qty = int(raw_qty)
            if qty < 0:
                raise ValueError
        except ValueError:
            self.highlight_error("quantity", "Кількість має бути цілим невід'ємним числом (0, 1, 2...).")
            return None

        try:
            price = float(raw_price)
            if price < 0 or raw_price == "":
                raise ValueError
        except ValueError:
            self.highlight_error("price", "Ціна має бути невід'ємним числом (наприклад: 150.50 або 150,50).")
            return None

        if not raw_id:
            p_id = str(uuid.uuid4())[:6].upper()
        else:
            p_id = raw_id

        for p in self.products:
            if p.id == p_id:
                if is_update and p_id == self.selected_id:
                    continue
                self.highlight_error("id", f"Товар із ID '{p_id}' вже існує! Вкажіть унікальний ID.")
                return None

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if is_update and self.selected_id:
            existing = next((p for p in self.products if p.id == self.selected_id), None)
            if existing:
                created_at = existing.created_at

        return Product(p_id, name, category, qty, price, location, created_at)

    def refresh_table(self):
        query = self.search_var.get().strip().lower()

        for row in self.tree.get_children():
            self.tree.delete(row)

        shown_count = 0
        for p in self.products:
            if query and (query not in p.name.lower() and query not in p.category.lower()):
                continue
            self.tree.insert(
                "",
                tk.END,
                iid=p.id,
                values=(p.id, p.name, p.category, p.quantity, f"{p.price:.2f}", p.location, p.created_at),
            )
            shown_count += 1

    def sort_by_column(self, col: str):
        reverse = self.sort_reverse.get(col, False)
        self.products.sort(key=lambda p: getattr(p, col), reverse=reverse)
        self.sort_reverse[col] = not reverse
        self.refresh_table()
        direction = "спаданням" if reverse else "зростанням"
        self.set_status(f"Відсортовано за '{col}' за {direction}.")

    def on_row_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        product = next((p for p in self.products if p.id == item_id), None)
        if not product:
            return

        self.reset_highlights()
        self.selected_id = product.id

        values_map = {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "quantity": str(product.quantity),
            "price": f"{product.price:.2f}",
            "location": product.location,
        }
        for key, val in values_map.items():
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, val)

        self.set_status(f"Вибрано товар '{product.name}' (ID: {product.id}).")

    def on_add(self):
        product = self._validate_and_build(is_update=False)
        if not product:
            return

        self.products.append(product)
        self.refresh_table()
        self.clear_form()
        self.set_status(f"Додано товар '{product.name}' (ID: {product.id}).")

    def on_update(self):
        if not self.selected_id:
            self.set_status("Спочатку виберіть рядок у таблиці для оновлення.", is_error=True)
            return

        updated_product = self._validate_and_build(is_update=True)
        if not updated_product:
            return

        for idx, p in enumerate(self.products):
            if p.id == self.selected_id:
                self.products[idx] = updated_product
                break

        self.selected_id = updated_product.id
        self.refresh_table()
        self.tree.selection_set(updated_product.id)
        self.set_status(f"Запис '{updated_product.name}' успішно оновлено.")

    def on_delete(self):
        if not self.selected_id:
            self.set_status("Спочатку виберіть рядок у таблиці для видалення.", is_error=True)
            return

        product = next((p for p in self.products if p.id == self.selected_id), None)
        if not product:
            return

        confirm = messagebox.askyesno(
            "Підтвердження видалення",
            f"Ви дійсно бажаєте видалити товар:\n«{product.name}» (ID: {product.id})?"
        )
        if not confirm:
            self.set_status("Видалення скасовано.")
            return

        self.products = [p for p in self.products if p.id != self.selected_id]
        self.refresh_table()
        self.clear_form()
        self.set_status(f"Товар '{product.name}' видалено.")

    def on_open(self):
        filepath = filedialog.askopenfilename(
            title="Відкрити файл обліку",
            filetypes=[("CSV файли", "*.csv"), ("Усі файли", "*.*")]
        )
        if not filepath:
            return

        try:
            loaded_products = self.storage.load(filepath)
            self.products = loaded_products
            self.current_filepath = filepath
            self.clear_form()
            self.refresh_table()
            self.set_status(f"Завантажено {len(self.products)} записів із '{os.path.basename(filepath)}'.")
        except Exception as e:
            messagebox.showerror("Помилка відкриття файлу", str(e))
            self.set_status(f"Не вдалося завантажити файл: {e}", is_error=True)

    def on_save(self):
        if not self.current_filepath:
            self.on_save_as()
            return
        self._save_to_path(self.current_filepath)

    def on_save_as(self):
        filepath = filedialog.asksaveasfilename(
            title="Зберегти як CSV",
            defaultextension=".csv",
            filetypes=[("CSV файли", "*.csv"), ("Усі файли", "*.*")]
        )
        if not filepath:
            return
        self._save_to_path(filepath)

    def _save_to_path(self, filepath: str):
        try:
            self.storage.save(filepath, self.products)
            self.current_filepath = filepath
            self.set_status(f"Збережено {len(self.products)} записів у '{os.path.basename(filepath)}'.")
        except Exception as e:
            messagebox.showerror("Помилка збереження", str(e))
            self.set_status(f"Помилка при збереженні: {e}", is_error=True)


if __name__ == "__main__":
    root = tk.Tk()
    storage_backend = CsvStorage()
    app = InventoryApp(root, storage_backend)
    root.mainloop()