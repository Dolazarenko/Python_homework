"""Метаклас TrackedMeta та декоратор log_call для логування роботи системи."""
from __future__ import annotations

import functools
import logging
import threading
from typing import Any, Callable, TypeVar

from .exceptions import LibraryError

logger = logging.getLogger("library.objects")
F = TypeVar("F", bound=Callable[..., Any])


class TrackedMeta(type):
    """Метаклас для всіх моделей бібліотеки.

    Виконує два завдання:
      1. Реєструє кожен визначений клас у словнику ``registry``.
      2. Перехоплює виклик ``Клас(...)`` і логує створення екземпляра з
         порядковим номером для цього класу. Лічильники захищені блокуванням,
         тож коректно працюють, коли об'єкти створюються з різних потоків.

    Якщо ``__init__`` кине виняток, об'єкт не вважається створеним:
    логування й підрахунок відбуваються лише після успішного завершення.
    """

    registry: dict[str, type] = {}
    _counters: dict[type, int] = {}
    _lock = threading.Lock()

    def __new__(mcls, name: str, bases: tuple, namespace: dict, **kwargs: Any):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        mcls.registry[name] = cls
        return cls

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        instance = super().__call__(*args, **kwargs)
        with TrackedMeta._lock:
            number = TrackedMeta._counters.get(cls, 0) + 1
            TrackedMeta._counters[cls] = number
        logger.info("Створено %s #%d", cls.__name__, number)
        return instance

    @classmethod
    def instances_created(mcls, cls: type) -> int:
        """Кількість успішно створених екземплярів заданого класу."""
        with mcls._lock:
            return mcls._counters.get(cls, 0)


def log_call(func: F) -> F:
    """Декоратор методів сервісу: логує бізнес-помилки і пробрасує їх далі."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except LibraryError as exc:
            logger.warning("%s: %s", func.__qualname__, exc)
            raise

    return wrapper  # type: ignore[return-value]
