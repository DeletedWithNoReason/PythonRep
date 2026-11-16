import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description="Аналіз даних поставок медикаментів.")
    parser.add_argument(
        "file",
        nargs="?",
        default="supplies.csv",
        help="Шлях до вхідного CSV файлу (за замовчуванням: supplies.csv)"
    )
    args = parser.parse_args()

    df = pd.read_csv(args.file)

    mean_price = np.mean(df["price_per_unit"])
    median_quantity = np.median(df["quantity"])
    std_price = np.std(df["price_per_unit"])

    print("--- Базова статистика (NumPy) ---")
    print(f"Середня ціна препаратів: {mean_price:.2f}")
    print(f"Медіана кількості (quantity): {median_quantity:.2f}")
    print(f"Стандартне відхилення ціни: {std_price:.2f}\n")

    df["total_price"] = df["quantity"] * df["price_per_unit"]

    supplier_revenue = df.groupby("supplier")["total_price"].sum()
    top_supplier = supplier_revenue.idxmax()
    top_supplier_value = supplier_revenue.max()

    category_quantity = df.groupby("category")["quantity"].sum()

    low_supply_filename = "low_supply.csv"
    low_supply_df = df[df["quantity"] < 100]
    low_supply_df.to_csv(low_supply_filename, index=False)

    print("--- Аналітика (pandas) ---")
    print(f"Постачальник з найбільшим прибутком: {top_supplier} ({top_supplier_value:.2f})")
    print("\nСумарна кількість препаратів за категоріями:")
    print(category_quantity.to_string(), "\n")

    top_3_supplies = df.sort_values(by="total_price", ascending=False).head(3)
    print("--- Топ-3 поставки за загальною вартістю ---")
    print(top_3_supplies.to_string(index=False), "\n")

    report_filename = "report.txt"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("ЗВІТ З АНАЛІЗУ ПОСТАВОК\n")
        f.write("=" * 30 + "\n")
        f.write(f"Середня ціна препаратів: {mean_price:.2f}\n")
        f.write(f"Медіана кількості: {median_quantity:.2f}\n")
        f.write(f"Стандартне відхилення ціни: {std_price:.2f}\n")
        f.write(f"Постачальник з найбільшим прибутком: {top_supplier} ({top_supplier_value:.2f})\n")
        f.write(f"Файл із дефіцитними поставками: {low_supply_filename}\n")

    print(f"Звіт успішно збережено у '{report_filename}', дефіцитні поставки — у '{low_supply_filename}'.")

    plt.figure(figsize=(8, 5))
    bars = plt.bar(category_quantity.index, category_quantity.values, color=["#4C72B0", "#55A868", "#C44E52"])
    plt.title("Розподіл кількості препаратів за категоріями")
    plt.xlabel("Категорія препарату")
    plt.ylabel("Загальна кількість (шт.)")
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 15, int(yval), ha="center", va="bottom")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()