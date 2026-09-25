"""Точка входу пакета ``shop_system``: демонстрація Завдань 1-4.

Запуск як самостійної програми (з кореневої директорії проекту)::

    python -m shop_system

Різниця між прямим запуском і імпортом: коли цей файл виконується
безпосередньо, Python встановлює ``__name__ == "__main__"`` і код у
блоці ``if __name__ == "__main__":`` виконується; якщо ж пакет лише
імпортують (``import shop_system``), ``__name__`` дорівнює
``"shop_system.__main__"``, і функція ``main()`` автоматично НЕ
викликається — це дозволяє використовувати пакет і як бібліотеку.
"""

from __future__ import annotations

import logging
import os

# Абсолютний імпорт цілого модуля (Завдання 3).
import shop_system.utils.file_tools as file_tools

# Вибірковий імпорт конкретних імен (Завдання 3).
from shop_system.models import (
    AppError,
    BusinessLogicError,
    ConfigLoadError,
    Product,
    ResourceNotFoundError,
    ValidationError,
)
from shop_system.services import InventoryService, OrderService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CATALOG_PATH = os.path.join(DATA_DIR, "products.json")
BROKEN_CATALOG_PATH = os.path.join(DATA_DIR, "broken.json")
MISSING_CATALOG_PATH = os.path.join(DATA_DIR, "does_not_exist.json")


def print_header(title: str) -> None:
    """Друкує вирівняний заголовок розділу для читабельного консольного виводу.

    Args:
        title: Назва розділу демонстрації (наприклад, ``"ЗАВДАННЯ 1"``).
    """
    width = 70
    print(f"\n{'═' * width}\n {title}\n{'═' * width}")


def print_step(label: str, message: str) -> None:
    """Друкує один крок демонстрації з коротким позначенням сценарію.

    Args:
        label: Позначення кроку/сценарію (наприклад, ``"Сценарій 1"``).
        message: Текст повідомлення.
    """
    print(f"  · [{label}] {message}")


def print_outcome(is_success: bool, message: str) -> None:
    """Друкує результат кроку з візуальною позначкою успіху/помилки.

    Args:
        is_success: ``True`` для успішного шляху, ``False`` для помилкового.
        message: Опис результату.
    """
    mark = "✔ УСПІХ " if is_success else "✘ ПОМИЛКА"
    print(f"    {mark} — {message}")


def demo_task1_exception_scenarios() -> InventoryService:
    """Демонстрація ЗАВДАННЯ 1: три сценарії обробки виключень + контекстний менеджер."""
    print_header("ЗАВДАННЯ 1 — Обробка виключень (try/except/else/finally)")
    inventory = InventoryService()

    # --- Сценарій 2: try/except/else/finally + контекстний менеджер ---
    print_step("Сценарій 2", "завантаження каталогу — успішний шлях")
    inventory.load_catalog(CATALOG_PATH)
    print_outcome(True, f"каталог завантажено, товарів: {len(inventory.catalog)}")

    print_step("Сценарій 2", "завантаження каталогу — файл відсутній")
    try:
        inventory.load_catalog(MISSING_CATALOG_PATH)
    except ConfigLoadError as exc:
        print_outcome(False, f"{exc}  (__cause__: {exc.__cause__!r})")

    print_step("Сценарій 2", "завантаження каталогу — некоректний JSON")
    try:
        inventory.load_catalog(BROKEN_CATALOG_PATH)
    except ConfigLoadError as exc:
        print_outcome(False, f"{exc}  (__cause__: {exc.__cause__!r})")

    # --- Сценарій 1: базовий try/except ---
    print_step("Сценарій 1", "парсинг кількості '10'")
    inventory.parse_quantity("10")
    print_outcome(True, "quantity=10")

    print_step("Сценарій 1", "парсинг кількості 'десять'")
    try:
        inventory.parse_quantity("десять")
    except ValidationError as exc:
        print_outcome(False, str(exc))

    # --- Сценарій 3: except (KeyError, TypeError) в одному блоці ---
    price_map = {"p1": 199.99}

    print_step("Сценарій 3", "пошук ціни наявного товару 'p1'")
    inventory.get_product_price(price_map, "p1")
    print_outcome(True, "price=199.99")

    print_step("Сценарій 3", "пошук ціни неіснуючого товару (KeyError)")
    try:
        inventory.get_product_price(price_map, "unknown")
    except ResourceNotFoundError as exc:
        print_outcome(False, str(exc))

    print_step("Сценарій 3", "пошук ціни у некоректній структурі (TypeError)")
    try:
        inventory.get_product_price(None, "p1")  # type: ignore[arg-type]
    except ResourceNotFoundError as exc:
        print_outcome(False, str(exc))

    return inventory


def demo_task2_hierarchy_and_reraise(inventory: InventoryService) -> None:
    """Демонстрація ЗАВДАННЯ 2: ієрархія виключень, ланцюжок і повторне піднесення."""
    print_header("ЗАВДАННЯ 2 — Ієрархія виключень, raise ... from ..., re-raise")
    order_service = OrderService(inventory)

    print_step("Замовлення", "оформлення 1 шт. товару 'p1' — успішний шлях")
    order_service.place_order("p1", 1)
    print_outcome(True, "замовлення оформлено")

    print_step("Ієрархія", "перехоплення конкретного типу vs базового класу")
    OrderService.demonstrate_hierarchy_catching(
        [
            ValidationError("некоректне значення", field_name="quantity"),
            BusinessLogicError("немає товару", error_code="INSUFFICIENT_STOCK"),
        ]
    )

    print_step("Re-raise", "логування помилки та повторне піднесення (raise без аргументів)")
    try:
        order_service.place_order_with_logging("unknown", 1)
    except AppError as exc:
        print_outcome(False, f"{exc}  |  to_dict()={exc.to_dict()}")


def demo_task3_module_behavior() -> None:
    """Демонстрація ЗАВДАННЯ 3: різниця між прямим запуском і імпортом модуля."""
    print_header("ЗАВДАННЯ 3 — Модулі, пакети, __name__ == '__main__'")
    print(f"  Поточне значення __name__ у цьому файлі: {__name__!r}")
    print(
        "  Якщо цей файл імпортувати (наприклад, `import shop_system.__main__`),\n"
        "  __name__ дорівнюватиме 'shop_system.__main__', і main() НЕ виконається автоматично."
    )
    print(f"  Абсолютний імпорт цілого модуля: file_tools -> {file_tools.__name__}")


def demo_task4_introspection() -> None:
    """Демонстрація ЗАВДАННЯ 4: docstrings, анотації типів, help()."""
    print_header("ЗАВДАННЯ 4 — Документування та інтроспекція")
    print("  --- help(InventoryService.parse_quantity) ---")
    help(InventoryService.parse_quantity)

    print(f"\n  Product.__doc__         -> {Product.__doc__.strip().splitlines()[0]!r}")
    print(
        "  file_tools.read_text_file_with_context_manager.__name__ -> "
        f"{file_tools.read_text_file_with_context_manager.__name__!r}"
    )
    print(
        "  InventoryService.parse_quantity.__annotations__ -> "
        f"{InventoryService.parse_quantity.__annotations__}"
    )
    print(
        "  OrderService.place_order.__annotations__         -> "
        f"{OrderService.place_order.__annotations__}"
    )


def main() -> None:
    """Головна функція: послідовно запускає демонстрації Завдань 1, 2, 3, 4."""
    inventory = demo_task1_exception_scenarios()
    demo_task2_hierarchy_and_reraise(inventory)
    demo_task3_module_behavior()
    demo_task4_introspection()
    print("\n" + "═" * 70)


if __name__ == "__main__":
    main()
