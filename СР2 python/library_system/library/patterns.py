"""Патерни проєктування: Observer (шина подій) та Strategy (політики позичання)."""
from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable

from .models import Reader

logger = logging.getLogger("library.events")

Handler = Callable[[dict[str, Any]], None]


class EventBus:
    """Observer: видавець подій, на які підписуються незалежні обробники.

    Збій одного обробника не блокує решту і не перериває операцію, що спричинила
    подію: сповіщення є другорядною дією відносно основної бізнес-логіки.
    """

    def __init__(self) -> None:
        self._handlers: defaultdict[str, list[Handler]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event: str, handler: Handler) -> None:
        with self._lock:
            self._handlers[event].append(handler)

    def publish(self, event: str, payload: dict[str, Any]) -> None:
        with self._lock:
            handlers = list(self._handlers.get(event, ()))  # копія під блокуванням
        for handler in handlers:
            try:
                handler(payload)
            except Exception:  # ізоляція підписників
                logger.exception("Обробник події %r завершився помилкою", event)


class LoanPolicy(ABC):
    """Strategy: правило, скільки книг одночасно може мати читач."""

    @abstractmethod
    def max_loans(self, reader: Reader) -> int:
        """Максимальна кількість одночасних позичок для читача."""

    def allows(self, reader: Reader) -> bool:
        return len(reader.borrowed_ids) < self.max_loans(reader)


class StandardPolicy(LoanPolicy):
    """Однаковий ліміт для всіх читачів."""

    def __init__(self, limit: int = 3) -> None:
        if limit < 1:
            raise ValueError("Ліміт позичок має бути щонайменше 1")
        self._limit = limit

    def max_loans(self, reader: Reader) -> int:
        return self._limit
