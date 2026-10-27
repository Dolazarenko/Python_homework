"""Демонстрація: навіщо потрібне блокування під час позичання.

Сценарій: 30 читачів одночасно беруть ту саму книгу. Затримка 1 мс у перевірці
політики (між перевіркою доступності та позначенням книги) відтворює реальну
ситуацію, коли перевірка звертається до зовнішнього сховища.
Запускається двічі: без блокування запису (гонка) і з ним (коректно).
"""
import contextlib
import logging
import time

from library import LibraryService, StandardPolicy
from library.concurrency import run_requests
from library.validators import make_isbn13

ROUNDS = 20
READERS = 30
WORKERS = 15


class SlowPolicy(StandardPolicy):
    """Політика з повільною перевіркою. Викликається між перевіркою доступності
    книги і її позначенням як виданої, тож розширює вікно для гонки."""

    def allows(self, reader):
        time.sleep(0.001)
        return super().allows(reader)


def one_round(use_lock: bool) -> int:
    """Повертає кількість читачів, яким вдалося позичити книгу (має бути 1)."""
    lib = LibraryService(policy=SlowPolicy(limit=3), latency=0.001)
    if not use_lock:
        lib._write_lock = contextlib.nullcontext()  # імітація версії без блокування
    author = lib.add_author("Автор")
    book = lib.add_book("Спірна книга", make_isbn13("000000001"), 2000, author)
    readers = [lib.register_reader(f"Ч{i}", f"race{i}@lib.ua") for i in range(READERS)]
    results = run_requests(
        [lambda r=r: lib.borrow_book(r.id, book.id) for r in readers],
        max_workers=WORKERS,
    )
    return sum(r.ok for r in results)


def main() -> None:
    logging.disable(logging.CRITICAL)  # приглушуємо логи відмов для чистого виводу
    for use_lock, label in ((False, "БЕЗ блокування"), (True, "З блокуванням")):
        outcomes = [one_round(use_lock) for _ in range(ROUNDS)]
        bad = sum(1 for n in outcomes if n != 1)
        print(f"{label:<16}: раундів={ROUNDS}, раундів з помилковим результатом={bad}, "
              f"максимум успішних позичок за раунд={max(outcomes)}")


if __name__ == "__main__":
    main()
