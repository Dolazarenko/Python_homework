"""Бенчмарк: послідовне і паралельне виконання запитів з імітованою затримкою сховища.

Затримка 2 мс на кожне звернення до сховища імітує диск або мережу. Без неї
операції в пам'яті виконуються занадто швидко, щоб виміряти ефект потоків
(через GIL паралельність дає виграш лише на операціях очікування, а не на CPU).
"""
import functools
import time

from library import LibraryService
from library.concurrency import run_requests
from library.validators import make_isbn13

LATENCY = 0.002   # секунд на одне звернення до сховища
QUERIES = 400
WORKERS = 8


def build_library():
    lib = LibraryService(latency=LATENCY)
    author = lib.add_author("Benchmark")
    book_ids, reader_ids = [], []
    for i in range(QUERIES):
        book_ids.append(lib.add_book(f"Книга {i}", make_isbn13(f"{i:09d}"), 2000, author).id)
        reader_ids.append(lib.register_reader(f"Читач {i}", f"b{i}@lib.ua").id)
    return lib, book_ids, reader_ids


def measure(requests, workers):
    started = time.perf_counter()
    results = run_requests(requests, max_workers=workers)
    elapsed = time.perf_counter() - started
    return elapsed, sum(r.ok for r in results)


def bench_search(workers):
    lib, _, _ = build_library()
    requests = [functools.partial(lib.search_books, "Книга 1") for _ in range(QUERIES)]
    return measure(requests, workers)


def bench_borrow(workers):
    lib, book_ids, reader_ids = build_library()
    requests = [functools.partial(lib.borrow_book, r, b) for r, b in zip(reader_ids, book_ids)]
    return measure(requests, workers)


def main() -> None:
    print(f"Затримка сховища: {LATENCY * 1000:.0f} мс, запитів: {QUERIES}, потоків: {WORKERS}\n")
    header = f"{'Операція':<10}{'Послідовно, с':>15}{'Паралельно, с':>16}{'Прискорення':>13}{'Успішних':>11}"
    print(header)
    print("-" * len(header))
    for name, bench in (("search", bench_search), ("borrow", bench_borrow)):
        t_seq, ok_seq = bench(1)
        t_par, ok_par = bench(WORKERS)
        print(f"{name:<10}{t_seq:>15.3f}{t_par:>16.3f}{t_seq / t_par:>12.2f}x{ok_par:>11}")


if __name__ == "__main__":
    main()
