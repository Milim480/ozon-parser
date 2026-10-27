import csv
from datetime import datetime


def save_to_csv(products, file_name):
    # Принимает список словарей и имя файла, записывает таблицу в CSV
    if not products:
        print("Нечего сохранять")
        return

    if not file_name.endswith(".csv"):
        file_name += ".csv"

    # одна и та же метка времени для всех строк этого запуска
    parsed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for product in products:
        product["parsed_at"] = parsed_at

    with open(file_name, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(products[0].keys()))
        writer.writeheader()
        writer.writerows(products)

    print(f"Сохранено товаров: {len(products)} -> {file_name}")

def print_report(products):
    # Показывает, сколько значений не удалось прочитать в каждом поле
    print(f"Собрано товаров: {len(products)}")
    for field in ["title", "price", "old_price", "rating", "reviews"]:
        missing = sum(p[field] is None for p in products)
        print(f"  без {field}: {missing}")