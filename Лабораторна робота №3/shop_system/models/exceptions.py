"""Ієрархія доменних виключень системи управління замовленнями.

Завдання 2. Усі виключення цього модуля наслідують від :class:`AppError`,
який, у свою чергу, наслідує від ``Exception`` (а не ``BaseException``,
щоб не перехоплювати системні сигнали ``SystemExit``/``KeyboardInterrupt``).

Схема ієрархії::

    Exception
     └── AppError                     (message, to_dict())
          ├── ValidationError         (+ field_name)
          ├── ResourceNotFoundError   (+ resource_id)
          ├── BusinessLogicError      (+ error_code)
          └── ConfigLoadError         (+ source_path)

Щоб уникнути дублювання коду в кожному підкласі, базовий клас сам уміє
зберігати "додаткові" іменовані атрибути (``extra``), автоматично
показувати їх у ``__str__`` та серіалізувати в ``to_dict()``. Завдяки
цьому кожен конкретний підклас — це лише кілька рядків: власний
конструктор із власною доменною назвою параметра.
"""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Базовий клас усіх доменних виключень застосунку.

    Args:
        message: Людинозрозумілий опис помилки.
        **extra: Додаткові доменні атрибути підкласу (наприклад,
            ``field_name`` у :class:`ValidationError`). Кожен переданий
            іменований аргумент одразу стає атрибутом екземпляра —
            саме так підкласи отримують "щонайменше один додатковий
            атрибут, специфічний для цього типу помилки".

    Attributes:
        message: Текст повідомлення про помилку.
    """

    def __init__(self, message: str, **extra: Any) -> None:
        super().__init__(message)
        self.message = message
        self._extra: dict[str, Any] = extra
        for name, value in extra.items():
            setattr(self, name, value)

    def __str__(self) -> str:
        details = ", ".join(f"{name}={value!r}" for name, value in self._extra.items())
        suffix = f" ({details})" if details else ""
        return f"[{self.__class__.__name__}] {self.message}{suffix}"

    def to_dict(self) -> dict[str, Any]:
        """Серіалізує виключення у словник (для логування чи передачі мережею).

        Returns:
            Словник із ключами ``type``, ``message`` та всіма доменними
            атрибутами конкретного підкласу.
        """
        return {"type": self.__class__.__name__, "message": self.message, **self._extra}


class ValidationError(AppError):
    """Помилка валідації вхідних даних певного поля.

    Attributes:
        field_name: Назва поля, яке не пройшло валідацію.
    """

    def __init__(self, message: str, field_name: str) -> None:
        super().__init__(message, field_name=field_name)


class ResourceNotFoundError(AppError):
    """Помилка відсутності ресурсу (наприклад, товару) за ідентифікатором.

    Attributes:
        resource_id: Ідентифікатор ресурсу, який не знайдено.
    """

    def __init__(self, message: str, resource_id: str) -> None:
        super().__init__(message, resource_id=resource_id)


class BusinessLogicError(AppError):
    """Помилка порушення бізнес-правила (наприклад, недостатньо товару на складі).

    Attributes:
        error_code: Внутрішній код бізнес-помилки.
    """

    def __init__(self, message: str, error_code: str) -> None:
        super().__init__(message, error_code=error_code)


class ConfigLoadError(AppError):
    """Помилка завантаження конфігурації/каталогу товарів із файлу.

    Attributes:
        source_path: Шлях до файлу, який не вдалося завантажити.
    """

    def __init__(self, message: str, source_path: str) -> None:
        super().__init__(message, source_path=source_path)
