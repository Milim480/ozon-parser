import time

from utils.browser import scroll_down
from utils.parsing import get_product_cards, get_product_url, parse_card

def collect_feed(driver, target=None, max_seconds=None,
                 products=None, seen=None, max_rounds=1000, patience=3):
    """Лента. Если переданы products и seen, продолжает с них."""
    if target is None and max_seconds is None:
        raise ValueError("Нужен хотя бы один лимит: target или max_seconds")

    products = products if products is not None else []
    seen = seen if seen is not None else set()

    # номера раундов продолжаются, а не начинаются с 1
    first_round = products[-1]["round"] + 1 if products else 1

    empty_rounds = 0
    start = time.time()

    for round_number in range(first_round, first_round + max_rounds):
        if max_seconds is not None and time.time() - start >= max_seconds:
            print("Время вышло")
            break

        cards = get_product_cards(driver.page_source)
        new_count = 0
        overlap = 0

        for card in cards:
            url = get_product_url(card)
            if url is None:
                continue

            if url in seen:
                overlap += 1
                continue

            seen.add(url)
            product = parse_card(card)
            product["round"] = round_number
            products.append(product)
            new_count += 1

            if target is not None and len(products) >= target:
                print(f"Набрано {len(products)} товаров")
                return products

        print(f"Раунд {round_number}: новых {new_count}, уже было {overlap}, всего {len(products)}")

        if round_number > first_round and overlap == 0:
            print("Внимание: нет пересечения с прошлым раундом, возможны пропуски")

        if new_count == 0:
            empty_rounds += 1
            if empty_rounds >= patience:
                print("Новые товары не появляются, категория исчерпана или страница зависла")
                break
        else:
            empty_rounds = 0

        scroll_down(driver, 5, pause=0.3)
        time.sleep(1.5)

    return products