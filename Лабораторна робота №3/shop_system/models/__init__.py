"""Підпакет ``models``: доменні моделі та ієрархія виключень (Завдання 2, 3).

Реекспортує ключові імена, щоб інші частини пакета могли робити
вибірковий імпорт: ``from shop_system.models import AppError, Product``.
"""

from shop_system.models.exceptions import (
    AppError,
    BusinessLogicError,
    ConfigLoadError,
    ResourceNotFoundError,
    ValidationError,
)
from shop_system.models.product import Product

__all__ = [
    "AppError",
    "ValidationError",
    "ResourceNotFoundError",
    "BusinessLogicError",
    "ConfigLoadError",
    "Product",
]
