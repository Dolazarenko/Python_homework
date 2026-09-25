"""Модуль домену: товар інтернет-магазину.

Docstring рівня модуля (Завдання 4).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Product:
    """Товар у каталозі інтернет-магазину.

    Args:
        product_id: Унікальний ідентифікатор товару.
        name: Назва товару.
        price: Ціна товару в гривнях.
        quantity: Кількість товару на складі.
    """

    product_id: str
    name: str
    price: float
    quantity: int

    def __str__(self) -> str:
        return f"{self.name} (id={self.product_id}): {self.quantity} шт. по {self.price} грн"

    @property
    def total_value(self) -> float:
        """Загальна вартість залишку товару на складі.

        Returns:
            Добуток ``price * quantity``.
        """
        return self.price * self.quantity
