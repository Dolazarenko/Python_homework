# practical_01_task_3_1.py

"""Використання циклу for для обчислень."""


def factorial(n: int) -> int:
    """Обчислює факторіал числа n."""
    result = 1
    for i in range(2, n + 1):  # range(start, stop)
        result *= i
    return result


def harmonic_sum(n: int) -> float:
    """Обчислює суму гармонічного ряду: 1 + 1/2 + 1/3 + ... + 1/n."""
    total = 0.0
    for i in range(1, n + 1):
        total += 1 / i
    return total


def multiplication_table(n: int) -> None:
    """Виводить таблицю множення n × n."""
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            print(f"{i * j:4d}", end="")
        print()


def main():
    n = int(input("Введіть число n: "))
    if n < 1:
        print("Помилка: n має бути натуральним числом")
        return
    print(f"{n}! = {factorial(n)}")
    print(f"Гармонічна сума H({n}) = {harmonic_sum(n):.6f}")
    print(f"\nТаблиця множення {n}×{n}:")
    multiplication_table(n)

    # Демонстрація range() зі step, у т.ч. від'ємним
    print(f"Парні числа до {n}: {list(range(2, n + 1, 2))}")
    print(f"Відлік вниз: {list(range(n, 0, -1))}")


if __name__ == "__main__":
    main()
