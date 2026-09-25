"""Сервіс оформлення замовлень.

Демонструє перехоплення виключень через конкретний підклас і через
базовий клас ієрархії, а також повторне піднесення (Завдання 2).

Docstring рівня модуля (Завдання 4).
"""

from __future__ import annotations

import logging

# Відносний імпорт між модулями одного підпакета services (Завдання 3).
from .inventory import InventoryService

# Вибірковий (іменований) абсолютний імпорт (Завдання 3).
from shop_system.models import AppError, BusinessLogicError, Product, ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class OrderService:
    """Сервіс оформлення замовлень покупців.

    Args:
        inventory: Сервіс каталогу товарів, з якого списується кількість.

    Attributes:
        inventory: Пов'язаний сервіс каталогу товарів.
    """

    def __init__(self, inventory: InventoryService) -> None:
        self.inventory = inventory

    def place_order(self, product_id: str, quantity: int) -> Product:
        """Оформлює замовлення: перевіряє наявність товару та кількість.

        Args:
            product_id: Ідентифікатор товару.
            quantity: Бажана кількість.

        Returns:
            Товар зі зменшеною кількістю на складі.

        Raises:
            ResourceNotFoundError: якщо товару немає в каталозі.
            BusinessLogicError: якщо на складі недостатньо товару.
        """
        if product_id not in self.inventory.catalog:
            raise ResourceNotFoundError("товар відсутній у каталозі", resource_id=product_id)
        product = self.inventory.catalog[product_id]
        if quantity > product.quantity:
            raise BusinessLogicError(
                f"недостатньо товару на складі (доступно {product.quantity})",
                error_code="INSUFFICIENT_STOCK",
            )
        product.quantity -= quantity
        return product

    def place_order_with_logging(self, product_id: str, quantity: int) -> Product:
        """Обгортка над ``place_order``, що логує помилку й повторно піднімає її.

        Демонструє повторне піднесення (``raise`` без аргументів,
        Завдання 2): обробник виконує побічну дію (логування у журнал),
        після чого передає те саме виключення далі по стеку зі
        збереженням оригінального traceback.

        Args:
            product_id: Ідентифікатор товару.
            quantity: Бажана кількість.

        Returns:
            Товар зі зменшеною кількістю на складі.

        Raises:
            AppError: будь-яка доменна помилка з ``place_order``, після логування.
        """
        try:
            return self.place_order(product_id, quantity)
        except AppError as exc:
            logger.error("Помилка оформлення замовлення: %s", exc.to_dict())
            raise  # повторне піднесення того самого виключення

    @staticmethod
    def demonstrate_hierarchy_catching(errors: list[AppError]) -> None:
        """Демонструє перехоплення як конкретного типу, так і через базовий клас.

        Args:
            errors: Список доменних виключень (екземплярів ``AppError``
                або його підкласів) для демонстрації обробки.
        """
        for error in errors:
            try:
                raise error
            except ValidationError as exc:
                print(f"    · перехоплено конкретний тип ValidationError: {exc}")
            except AppError as exc:
                print(f"    · перехоплено через базовий клас AppError:    {exc}")
