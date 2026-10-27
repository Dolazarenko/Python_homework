"""Мультипоточне виконання запитів до сервісу через пул потоків."""
from __future__ import annotations

import threading
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RequestResult:
    index: int                      # порядковий номер запиту у вхідному списку
    ok: bool                        # чи завершився запит без винятку
    value: Any = None               # результат, якщо ok=True
    error: Exception | None = None  # виняток, якщо ok=False
    thread: str = ""                # ім'я потоку, що виконав запит
    duration_ms: float = 0.0        # тривалість запиту в мілісекундах


def run_requests(
    requests: Iterable[Callable[[], Any]],
    max_workers: int = 8,
) -> list[RequestResult]:
    """Виконує запити у пулі потоків і повертає результати у порядку подання.

    Виняток одного запиту не зупиняє решту: він фіксується в RequestResult.
    """

    def _execute(index: int, request: Callable[[], Any]) -> RequestResult:
        started = time.perf_counter()
        thread = threading.current_thread().name
        try:
            value = request()
        except Exception as exc:  # будь-яка помилка фіксується, а не поширюється
            return RequestResult(index, False, error=exc, thread=thread,
                                 duration_ms=_elapsed_ms(started))
        return RequestResult(index, True, value=value, thread=thread,
                             duration_ms=_elapsed_ms(started))

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="req") as pool:
        futures = [pool.submit(_execute, i, req) for i, req in enumerate(requests)]
        return [future.result() for future in futures]


def _elapsed_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000
