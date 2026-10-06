"""Функції-генератори для числових послідовностей."""

from __future__ import annotations

import itertools


def arithmetic_progression(start: float, step: float):
    """Нескінченна арифметична прогресія."""
    current = start
    while True:
        yield current
        current += step


def geometric_progression(start: float, ratio: float, limit: float = float("inf")):
    """Геометрична прогресія, поки значення <= limit."""
    current = start
    while current <= limit:
        yield current
        current *= ratio


def fibonacci(n: int | None = None):
    """Числа Фібоначчі: n штук або нескінченно, якщо n is None."""
    a, b = 0, 1
    count = 0
    while n is None or count < n:
        yield a
        a, b = b, a + b
        count += 1


def collatz_sequence(n: int):
    """Послідовність Коллатца від n до 1 включно."""
    yield n
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        yield n


def flatten(nested):
    """Рекурсивне розгортання вкладених списків через yield from."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def main():
    ap = arithmetic_progression(2, 3)
    first_10 = list(itertools.islice(ap, 10))
    print(f"Арифметична прогресія (2, 3): {first_10}")

    gp = list(geometric_progression(1, 2, limit=1000))
    print(f"Геометрична прогресія (1, 2): {gp}")

    fib_15 = list(fibonacci(15))
    print(f"Фібоначчі (15): {fib_15}")

    coll = list(collatz_sequence(27))
    print(f"Коллатц (27): довжина={len(coll)}, макс={max(coll)}")

    nested = [1, [2, 3], [4, [5, 6]], 7, [8, [9, [10]]]]
    print(f"Розгортання: {list(flatten(nested))}")

    for fib_num in fibonacci(None):
        if fib_num > 10000:
            print(f"Перше число Фібоначчі > 10000: {fib_num}")
            break


if __name__ == "__main__":
    main()