from utils.browser import init_webdriver
from utils.collectors import collect_feed
from utils.storage import save_to_csv, print_report
import time

url = input("Ссылка: ")
mode = input("Собирать по: 1 - количеству, 2 - времени: ")
file_name = input("Имя файла (без .csv): ")

driver = init_webdriver()
try:
    driver.get(url)
    time.sleep(10)  # капча

    if mode == "1":
        target = int(input("Сколько товаров собрать: "))
        products = collect_feed(driver, target=target)

    else:
        # 1. Проба: 15 секунд, замеряем скорость
        products, seen = [], set()
        probe_start = time.time()
        collect_feed(driver, max_seconds=15, products=products, seen=seen)
        probe_time = time.time() - probe_start

        if not products:
            print("Проба ничего не собрала (возможно, капча)")
            exit()

        rate = len(products) / probe_time
        print(f"За {probe_time:.0f} с собрано {len(products)} (~{rate:.1f} товаров/с)")

        # 2. Пользователь выбирает время, видит прикидку и подтверждает
        while True:
            seconds = int(input("Сколько секунд всего собирать: "))
            estimate = int(rate * seconds)
            print(f"За {seconds} с получится примерно {estimate} товаров")

            answer = input("Enter - подходит, n - изменить время, q - задать количество: ")
            if answer == "":
                break
            if answer == "q":
                target = int(input("Сколько товаров собрать: "))
                products = collect_feed(driver, target=target, products=products, seen=seen)
                seconds = None
                break

        # 3. Основной сбор (пробные секунды уже потрачены)
        if seconds is not None:
            remaining = max(seconds - probe_time, 0)
            products = collect_feed(driver, max_seconds=remaining, products=products, seen=seen)
finally:
    driver.quit()

print_report(products)
save_to_csv(products, file_name)