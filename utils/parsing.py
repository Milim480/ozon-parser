import re
from utils.cleaning import clean_price
from bs4 import BeautifulSoup

def get_product_cards(page_source):
    """Принимает HTML (строку), возвращает список карточек без повторов."""
    soup = BeautifulSoup(page_source, "html.parser")

    cards = []
    seen = set()

    for link in soup.find_all("a", href=lambda h: h and "/product/" in h):
        # поднимаемся от ссылки к карточке
        card = link.find_parent(attrs={"data-index": True})
        if card is None:
            continue

        # у карточки две ссылки, вторую отсекаем
        if id(card) in seen:
            continue
        seen.add(id(card))
        cards.append(card)

    return cards


def parse_card(card):
    price, old_price, discount = get_price(card)
    return {
        "title": get_title(card),
        "price": price,
        "old_price": old_price,
        "discount": discount,
        "rating": get_rating(card),
        "reviews": get_reviews(card),
        "url": get_product_url(card),
    }


def get_product_url(card):
    link = card.find(
        "a",
        href=lambda href: href and "/product/" in href
    )

    if link is None:
        return None

    return "https://www.ozon.ru" + link.get("href").split("?")[0]


def get_price(card):
    """Принимает карточку, возвращает (цена, старая цена, скидка %).
    Если блока цен нет, возвращает (None, None, None)."""

    # 1. Идём вглубь карточки: карточка -> info -> блок цен
    info_blocks = card.find_all("div", recursive=False)
    if not info_blocks:
        return None, None, None

    price_blocks = info_blocks[0].find_all("div", recursive=False)
    if not price_blocks:
        return None, None, None

    # 2. Тексты "листовых" span-ов (без вложенных span-ов внутри)
    values = [
        span.get_text(strip=True)
        for span in price_blocks[0].find_all("span")
        if span.find("span") is None
    ]

    # временная отладка:
    # for i, v in enumerate(values):
    #     print(i, repr(v))

    # 3. Сортируем по содержимому, а не по номеру
    prices = []
    discount = 0

    for text in values:
        if "₽" in text:
            prices.append(clean_price(text))
        elif "%" in text:
            discount = clean_price(text)

    if not prices:
        return None, None, None

    price = prices[0]                                  # первая цена: текущая
    old_price = prices[1] if len(prices) > 1 else None  # вторая: старая (если есть)

    return price, old_price, discount

def get_texts(card):
    # Тексты всех "листовых" span-ов карточки, без пустых
    texts = []
    for span in card.find_all("span"):
        if span.find("span") is None:
            text = span.get_text(strip=True)
            if text:
                texts.append(text)
    return texts


def get_title(card):
    texts = []
    for t in get_texts(card):
        if "₽" in t:                        # цена
            continue
        if re.fullmatch(r"[−-]\d+%", t):    # скидка
            continue
        if "отзыв" in t:                    # число отзывов
            continue
        if re.fullmatch(r"\d\.\d", t):      # рейтинг
            continue
        texts.append(t)
    return max(texts, key=len) if texts else None


def get_rating(card):
    for text in get_texts(card):
        if re.fullmatch(r"\d\.\d", text):
            return float(text)
    return None


def get_reviews(card):
    for text in get_texts(card):
        if "отзыв" in text:
            return clean_price(text)
    return None
