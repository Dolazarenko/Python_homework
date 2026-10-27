"""Патерн Repository: потокобезпечне зберігання сутностей у пам'яті."""
from __future__ import annotations

import itertools
import threading
import time
from typing import Callable, Generic, TypeVar

from .exceptions import NotFoundError

T = TypeVar("T")


class Repository(Generic[T]):
    """Колекція сутностей з автоматичними ідентифікаторами.

    Параметр ``latency`` імітує затримку звернення до зовнішнього сховища
    (диск, мережа). Використовується лише в бенчмарку; за замовчуванням 0.
    Затримка виконується до взяття блокування, тож не блокує інші читання.
    """

    def __init__(self, entity_name: str, latency: float = 0.0) -> None:
        self._entity_name = entity_name
        self._latency = latency
        self._items: dict[int, T] = {}
        self._ids = itertools.count(1)
        self._lock = threading.RLock()

    def _simulate_io(self) -> None:
        if self._latency:
            time.sleep(self._latency)

    def add(self, item: T) -> T:
        with self._lock:
            item.id = next(self._ids)  # type: ignore[attr-defined]
            self._items[item.id] = item  # type: ignore[attr-defined]
            return item

    def get(self, item_id: int) -> T:
        self._simulate_io()
        with self._lock:
            try:
                return self._items[item_id]
            except KeyError:
                raise NotFoundError(f"{self._entity_name} з id={item_id} не знайдено") from None

    def find(self, predicate: Callable[[T], bool]) -> list[T]:
        self._simulate_io()
        with self._lock:
            return [item for item in self._items.values() if predicate(item)]

    def all(self) -> list[T]:
        self._simulate_io()
        with self._lock:
            return list(self._items.values())

    def remove(self, item_id: int) -> None:
        with self._lock:
            self._items.pop(item_id, None)

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)
