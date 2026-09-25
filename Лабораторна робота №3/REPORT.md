# Звіт до лабораторної роботи
## Реалізація обробки виключень, модульності та документації в проектах Python

**Предметна область:** система управління каталогом та замовленнями інтернет-магазину
(пакет `shop_system`).

---

## Завдання 1. Обробка виключень: try/except/else/finally

Реалізовано в `shop_system/services/inventory.py` (клас `InventoryService`).

| Сценарій | Метод | Конструкція | Перехоплювані типи | Чому саме ці типи |
|---|---|---|---|---|
| 1 | `parse_quantity` | базовий `try/except` | `ValueError` | `int()` піднімає саме `ValueError` при некоректному текстовому представленні числа |
| 2 | `load_catalog` | повний `try/except/else/finally` | `FileNotFoundError`, `json.JSONDecodeError` (окремими блоками) | це дві конкретні, різні за природою причини провалу читання конфігурації — відсутність файлу й невалідний вміст |
| 3 | `get_product_price` | один блок `except (KeyError, TypeError)` | `KeyError`, `TypeError` | обидві помилки з точки зору виклику означають одне: «неможливо дістати ціну з наданих даних» (немає ключа, або структура взагалі не підтримує індексацію за ключем) |

Ніде не використано «голий» `except:` і не перехоплюється `Exception` без потреби — кожен `except` типізований найвужчим доречним типом.

**Сценарій 2 детально** (`load_catalog`):
- `try` — відкриває файл через власний контекстний менеджер `JsonCatalogReader` (`with`) і читає JSON;
- `except FileNotFoundError` / `except json.JSONDecodeError` — виконується, якщо файл відсутній або містить некоректний JSON; у кожному випадку доменне виключення `ConfigLoadError` піднімається через `raise ... from ...`;
- `else` — виконується **лише** якщо в `try` не сталося жодного виключення; саме тут дані розпаковуються у `Product` та додаються в `self.catalog`;
- `finally` — виконується **завжди** (і при успіху, і при помилці) і друкує повідомлення про завершення спроби завантаження.

**Контекстний менеджер.** Клас `JsonCatalogReader` (`shop_system/utils/file_tools.py`) реалізує протокол `__enter__`/`__exit__`. Використання `with JsonCatalogReader(path) as reader:` гарантує виклик `__exit__` (а отже — закриття файлу) навіть якщо всередині блоку станеться виключення, без потреби писати `try/finally` вручну для звільнення ресурсу. Це надійніше за ручний `try: ... finally: f.close()`, бо неможливо забути закрити ресурс і код читання не «засмічується» логікою звільнення ресурсів.

Обидва потоки (успішний і помилковий) продемонстровано для кожного сценарію в `shop_system/__main__.py` — при запуску видно виведення й для коректних, і для некоректних вхідних даних (файли `data/products.json`, `data/broken.json`, неіснуючий шлях).

---

## Завдання 2. Ієрархія власних виключень та ланцюжки виключень

Файл: `shop_system/models/exceptions.py`.

### Схема ієрархії

```
Exception
 └── AppError                     (базовий клас застосунку; message, _extra, to_dict())
      ├── ValidationError         (+ field_name)
      ├── ResourceNotFoundError   (+ resource_id)
      ├── BusinessLogicError      (+ error_code)
      └── ConfigLoadError         (+ source_path)
```

Усього 5 класів (1 базовий + 4 конкретних), усі наслідують зрештою від `Exception` (не від `BaseException`).

**Як влаштовано без дублювання коду.** Замість того, щоб кожен підклас окремо перевизначав `__str__` і `to_dict()` (як у першій версії), базовий `AppError` сам приймає довільні іменовані аргументи (`**extra`), одразу робить їх атрибутами екземпляра та автоматично додає в текстове представлення й у `to_dict()`. Завдяки цьому кожен конкретний підклас — це буквально один рядок:

```python
class ValidationError(AppError):
    def __init__(self, message: str, field_name: str) -> None:
        super().__init__(message, field_name=field_name)
```

При цьому вимога «кожен підклас має щонайменше один додатковий атрибут» виконується так само: `exc.field_name`, `exc.resource_id`, `exc.error_code`, `exc.source_path` — усі доступні напряму. `to_dict()` — необов'язкове ускладнення для серіалізації помилки (наприклад, для журналювання чи передачі мережею) — тепер теж успадковується без повторення коду.

### Піднесення та перехоплення

- Кожен підклас піднімається у відповідній ситуації: `ValidationError` — при парсингу кількості; `ResourceNotFoundError` — коли товару немає в каталозі/ціновій мапі; `BusinessLogicError` — коли на складі недостатньо товару; `ConfigLoadError` — при провалі завантаження файлу каталогу.
- У `OrderService.demonstrate_hierarchy_catching` показано перехоплення **і** конкретного типу (`except ValidationError`), **і** всієї категорії через базовий клас (`except AppError`).

### Ланцюжок виключень (`raise ... from ...`)

У `InventoryService.load_catalog`: при перехопленні низькорівневих `FileNotFoundError`/`json.JSONDecodeError` піднімається `ConfigLoadError(...) from exc`. Це зберігає першопричину в атрибуті `__cause__`. У `shop_system/__main__.py` продемонстровано доступ до неї: `exc.__cause__` виводить оригінальний `FileNotFoundError`/`JSONDecodeError`.

### Повторне піднесення (`raise` без аргументів)

У `OrderService.place_order_with_logging`: перехоплюється `AppError`, виконується побічна дія (запис у журнал через `logging`), після чого виключення передається далі стеком через голий `raise` — без зміни типу й traceback.

---

## Завдання 3. Організація коду в модулі та пакети

### Дерево файлів проекту

```
shop_system_project/
├── requirements.txt                 # без залежностей (лише стандартна бібліотека)
├── REPORT.md                        # цей звіт
├── demo_star_import.py              # демонстрація `from shop_system import *`
└── shop_system/                     # головний пакет
    ├── __init__.py                  # реекспорт AppError, Product, InventoryService, OrderService; __all__
    ├── __main__.py                  # точка входу: python -m shop_system
    ├── data/
    │   ├── products.json            # коректний каталог товарів
    │   └── broken.json              # навмисно невалідний JSON (для демонстрації ConfigLoadError)
    ├── models/                      # підпакет: доменні моделі та виключення
    │   ├── __init__.py              # реекспорт + __all__
    │   ├── exceptions.py            # ієрархія AppError -> 4 підкласи
    │   └── product.py               # dataclass Product
    ├── services/                    # підпакет: бізнес-логіка
    │   ├── __init__.py              # реекспорт + __all__
    │   ├── inventory.py             # InventoryService: 3 сценарії обробки виключень
    │   └── order.py                 # OrderService: ієрархія, ланцюжок, re-raise
    └── utils/                       # підпакет: допоміжні функції
        ├── __init__.py              # реекспорт + __all__
        └── file_tools.py            # JsonCatalogReader (контекстний менеджер) та ін.
```

Разом: **3 підпакети** (`models`, `services`, `utils`) і **7 «змістовних» модулів** без урахування `__init__.py` — набагато більше мінімально вимогливих 2 підпакетів / 4 модулів.

### Три форми імпорту

1. **Абсолютний імпорт цілого модуля** — `shop_system/__main__.py`: `import shop_system.utils.file_tools as file_tools`.
2. **Вибірковий імпорт конкретних імен** — усюди в проекті, напр. `from shop_system.models import AppError, Product`.
3. **Відносний імпорт у межах пакета** — `shop_system/services/order.py`: `from .inventory import InventoryService` (посилання на сусідній модуль того самого підпакета).

### `__name__ == "__main__"`

Реалізовано в `shop_system/__main__.py`. При запуску `python -m shop_system` Python встановлює `__name__ == "__main__"`, і викликається `main()`, яка послідовно демонструє всі чотири завдання. Якщо ж пакет лише імпортують (`import shop_system` або `from shop_system import InventoryService`), жодного виведення в консоль не відбувається і жодна демонстраційна функція не запускається — пакет поводиться як бібліотека.

### `__all__` та `from package import *`

`shop_system/__init__.py` визначає `__all__ = ["AppError", "Product", "InventoryService", "OrderService"]`. Скрипт `demo_star_import.py` виконує `from shop_system import *` і звіряє список імпортованих імен зі списком `__all__` — фактичний результат запуску:

```
Імена, імпортовані через `from shop_system import *`:
['AppError', 'InventoryService', 'OrderService', 'Product']

Очікувані імена з shop_system.__all__: ['AppError', 'InventoryService', 'OrderService', 'Product']
Підтверджено: імпортовано рівно ті імена, що вказані в __all__.
```

Це підтверджує, що `__all__` реально обмежує експорт: приватні деталі реалізації (наприклад, внутрішні підмодулі) через зірковий імпорт не потрапляють у простір імен.

### Запуск проекту

З кореневої директорії `shop_system_project/`:

```bash
python -m shop_system            # повна демонстрація завдань 1, 2, 3, 4
python demo_star_import.py       # демонстрація __all__
```

Сторонні бібліотеки не використовуються — проєкт працює на стандартній бібліотеці Python 3.11+.

---

## Завдання 4. Документування коду: docstrings, анотації типів, інтроспекція

### Обраний стиль docstrings — **Google style**

Обґрунтування вибору:
- Google-стиль читається як звичайний текст навіть без рендерингу (секції `Args:`, `Returns:`, `Raises:` виділяються відступом, а не спецсимволами), що зручно при перегляді коду в IDE чи консолі (`help()`).
- Порівняно з reStructuredText він компактніший і менш «шумний» (без директив `:param:`, `:type:`, `:rtype:` для кожного параметра окремо).
- Порівняно з NumPy-стилем (секції з підкресленням `----------`) він займає менше вертикального простору, що доречно для проекту середнього розміру, як цей.
- Google-стиль добре підтримується інструментами (Sphinx через розширення `napoleon`, mypy для анотацій), тож сумісність із генераторами документації не втрачається.

### Порівняння стилів docstrings

| Стиль | Переваги | Обмеження |
|---|---|---|
| **Google** | Компактний, легко читається як звичайний текст, добре підтримується Sphinx (napoleon) | Менш строгий формат — легше зробити помилку в структурі секцій, яку інструменти не завжди підкажуть |
| **NumPy** | Дуже чіткий поділ секцій (підкреслення), зручний для документації з великою кількістю параметрів і складними типами (наукові/дата-проекти) | Займає значно більше рядків на кожну функцію, надлишковий для невеликих утиліт |
| **reStructuredText** | Нативно підтримується Sphinx без додаткових розширень, максимально точна прив'язка типів (`:type:`, `:rtype:`) | Найменш читабельний у «сирому» вигляді (директиви `:param:`/`:raises:` захаращують текст), багатослівний |

### Docstrings і анотації типів

- Усі публічні класи, методи й функції пакета мають docstrings із описом призначення, параметрів, значення, що повертається, та секцією `Raises` (де це доречно) — стиль єдиний (Google) у межах усього проекту.
- Docstring рівня модуля додано щонайменше до двох модулів: `shop_system/models/exceptions.py` та `shop_system/services/inventory.py` (фактично — до всіх модулів пакета).
- Анотації типів присутні щонайменше у 5 функціях/методах, зокрема з використанням вбудованих параметризованих типів (`dict[str, Product]`, `list[dict[str, Any]]`) та типів з `typing` (`Optional[...]`, `Any`):
  - `InventoryService.parse_quantity(self, raw_value: str) -> int`
  - `InventoryService.get_product_price(self, price_map: dict, product_id: str) -> float`
  - `InventoryService.load_catalog(self, path: str) -> None`
  - `OrderService.place_order(self, product_id: str, quantity: int) -> Product`
  - `OrderService.place_order_with_logging(self, product_id: str, quantity: int) -> Product`
  - `JsonCatalogReader.read(self) -> list[dict[str, Any]]`
  - `AppError.to_dict(self) -> dict[str, Any]`

### Інтроспекція — приклад виводу `help()`

Консоль тепер оформлена зрозуміліше: кожен розділ демонстрації позначено рамкою-заголовком (`════`), кожен крок — міткою сценарію (`· [Сценарій N] ...`), а результат — позначкою `✔ УСПІХ` / `✘ ПОМИЛКА`, щоб одразу було видно, який шлях (успішний чи помилковий) виконується.

Виклик `help(InventoryService.parse_quantity)` (див. `shop_system/__main__.py`, `demo_task4_introspection`) виводить:

```
Help on function parse_quantity in module shop_system.services.inventory:

parse_quantity(self, raw_value: 'str') -> 'int'
    Парсить кількість товару з рядка.

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
```

Додатково продемонстровано:
- `Product.__doc__` → `"Товар у каталозі інтернет-магазину."`
- `file_tools.read_text_file_with_context_manager.__name__` → `'read_text_file_with_context_manager'`
- `InventoryService.parse_quantity.__annotations__` → `{'raw_value': 'str', 'return': 'int'}`
- `OrderService.place_order.__annotations__` → `{'product_id': 'str', 'quantity': 'int', 'return': 'Product'}`

---

## Підсумок відповідності критеріям

| № | Завдання | Статус |
|---|---|---|
| 1 | 3 сценарії обробки виключень, контекстний менеджер, обидва шляхи | ✅ |
| 2 | Ієрархія з 5 класів, додаткові атрибути, `raise ... from ...`, re-raise, схема | ✅ |
| 3 | 3 підпакети / 7 модулів, 3 форми імпорту, `__init__.py` з `__all__`, `__main__`, requirements.txt | ✅ |
| 4 | Docstrings (Google) для всього публічного API, ≥5 анотованих функцій, `help()`, порівняння стилів | ✅ |
