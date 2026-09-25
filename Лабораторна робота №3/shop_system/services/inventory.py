"""Сервіс управління каталогом товарів.

Містить три сценарії обробки виключень (Завдання 1) та демонстрацію
ланцюжка виключень ``raise ... from ...`` (Завдання 2).

Docstring рівня модуля (Завдання 4).
"""

from __future__ import annotations

import json

from shop_system.models import ConfigLoadError, Product, ResourceNotFoundError, ValidationError
from shop_system.utils import JsonCatalogReader


class InventoryService:
    """Сервіс для роботи з каталогом товарів.

    Attributes:
        catalog: Словник товарів ``product_id -> Product``.
    """

    def __init__(self) -> None:
        self.catalog: dict[str, Product] = {}

    # ------------------------------------------------------------------
    # Сценарій 2 (Завдання 1): try/except/else/finally + контекстний менеджер
    # ------------------------------------------------------------------
    def load_catalog(self, path: str) -> None:
        """Завантажує каталог товарів із JSON-файлу.

        Сценарій 2 — повна конструкція ``try/except/else/finally``:
        блок ``try`` намагається відкрити й розпарсити файл через
        власний контекстний менеджер ``JsonCatalogReader``; блоки
        ``except`` перехоплюють конкретні очікувані помилки читання
        (``FileNotFoundError``, ``json.JSONDecodeError``) і піднімають
        доменну ``ConfigLoadError`` через ланцюжок ``raise ... from ...``
        (Завдання 2), зберігаючи первинну причину в ``__cause__``;
        блок ``else`` виконується лише тоді, коли парсинг пройшов без
        жодного виключення, і саме там дані потрапляють у каталог;
        блок ``finally`` виконується завжди — і при успіху, і при
        помилці — та друкує діагностичне повідомлення про завершення
        спроби завантаження.

        Args:
            path: Шлях до JSON-файлу каталогу.

        Raises:
            ConfigLoadError: якщо файл відсутній або містить некоректний JSON.
        """
        print(f"[Сценарій 2] Спроба завантажити каталог з '{path}'")
        try:
            with JsonCatalogReader(path) as reader:
                raw_items = reader.read()
        except FileNotFoundError as exc:
            raise ConfigLoadError("файл каталогу не знайдено", source_path=path) from exc
        except json.JSONDecodeError as exc:
            raise ConfigLoadError(f"некоректний JSON: {exc}", source_path=path) from exc
        else:
            # Виконується лише за відсутності виключень у try — «успішний шлях».
            for item in raw_items:
                product = Product(**item)
                self.catalog[product.product_id] = product
            print(f"[Сценарій 2] Успішний шлях: завантажено {len(self.catalog)} товар(ів)")
        finally:
            # Виконується завжди, незалежно від результату спроби.
            print("[Сценарій 2] Завершено спробу завантаження каталогу")

    # ------------------------------------------------------------------
    # Сценарій 1 (Завдання 1): базовий try/except
    # ------------------------------------------------------------------
    def parse_quantity(self, raw_value: str) -> int:
        """Парсить кількість товару з рядка.

        Сценарій 1 — базовий ``try/except``: перехоплюється лише
        ``ValueError``, бо саме це виключення піднімає ``int()`` при
        некоректному текстовому представленні числа. Інші типи помилок
        навмисно не перехоплюються, щоб не приховувати непередбачені
        дефекти під загальним ``except Exception``.

        Args:
            raw_value: Рядкове представлення кількості.

        Returns:
            Ціле число — кількість товару.

        Raises:
            ValidationError: якщо ``raw_value`` не є цілим числом.
        """
        print(f"[Сценарій 1] Парсинг кількості: '{raw_value}'")
        try:
            quantity = int(raw_value)
        except ValueError as exc:
            raise ValidationError(f"'{raw_value}' не є цілим числом", field_name="quantity") from exc
        print(f"[Сценарій 1] Успішний шлях: quantity={quantity}")
        return quantity

    # ------------------------------------------------------------------
    # Сценарій 3 (Завдання 1): except (Type1, Type2)
    # ------------------------------------------------------------------
    def get_product_price(self, price_map: dict, product_id: str) -> float:
        """Повертає ціну товару, обробляючи кілька типів помилок одним блоком.

        Сценарій 3 — ``except (KeyError, TypeError)``: ``KeyError``
        виникає, якщо товару немає у переданому словнику ``price_map``,
        а ``TypeError`` — якщо замість словника передано непідтримуваний
        тип (наприклад, ``None``). Обидва випадки з точки зору виклику
        означають одне й те саме: «неможливо визначити ціну з наданих
        даних», тому їх логічно обробляти в одному блоці.

        Args:
            price_map: Словник ``{product_id: price}`` або інша структура.
            product_id: Ідентифікатор товару.

        Returns:
            Ціна товару.

        Raises:
            ResourceNotFoundError: якщо ціну товару неможливо визначити.
        """
        print(f"[Сценарій 3] Пошук ціни товару '{product_id}'")
        try:
            price = price_map[product_id]
        except (KeyError, TypeError) as exc:
            raise ResourceNotFoundError(
                "не вдалося визначити ціну товару", resource_id=product_id
            ) from exc
        print(f"[Сценарій 3] Успішний шлях: price={price}")
        return price
