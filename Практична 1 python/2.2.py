# practical_01_task_2_2.py

"""Визначення типу трикутника та обчислення площі."""

import math


def triangle_type(a: float, b: float, c: float) -> str:
    """Визначає тип трикутника за сторонами.

    Returns:
        Рядок з типом: 'рівносторонній', 'рівнобедрений',
        'прямокутний', 'різносторонній' або 'не є трикутником'.
    """
    # Нерівність трикутника
    if not (a > 0 and b > 0 and c > 0
            and a + b > c and a + c > b and b + c > a):
        return "не є трикутником"

    if a == b == c:
        return "рівносторонній"

    # Прямокутність: гіпотенуза — найбільша сторона
    x, y, z = sorted((a, b, c))
    if abs(x ** 2 + y ** 2 - z ** 2) < 1e-9:
        return "прямокутний"
    elif a == b or b == c or a == c:
        return "рівнобедрений"
    else:
        return "різносторонній"


def triangle_area(a: float, b: float, c: float) -> float:
    """Обчислює площу трикутника за формулою Герона."""
    p = (a + b + c) / 2
    return math.sqrt(p * (p - a) * (p - b) * (p - c))


def main():
    try:
        a = float(input("Сторона a: "))
        b = float(input("Сторона b: "))
        c = float(input("Сторона c: "))
    except ValueError:
        print("Помилка: введіть числа")
        return

    t = triangle_type(a, b, c)
    print(f"Тип трикутника: {t}")
    if t != "не є трикутником":
        print(f"Площа: {triangle_area(a, b, c):.2f}")


if __name__ == "__main__":
    main()
