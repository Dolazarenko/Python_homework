"""Пакет ``shop_system`` — навчальний проект із обробки виключень,
модульності та документування коду (Завдання 1–4).

``__all__`` нижче визначає, які імена експортуються під час
``from shop_system import *`` (демонстрація — у ``demo_star_import.py``).
"""

from shop_system.models import AppError, Product
from shop_system.services import InventoryService, OrderService

__all__ = ["AppError", "Product", "InventoryService", "OrderService"]
