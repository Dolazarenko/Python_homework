# practical_01_task_1_1.py

"""Обчислення математичних виразів."""

import math


def main():
    # Зчитуємо три числа від користувача
    a = float(input("Введіть a: "))
    b = float(input("Введіть b: "))
    c = float(input("Введіть c: "))

    # 1. Сума квадратів
    sum_squares = a ** 2 + b ** 2 + c ** 2

    # 2. Середнє арифметичне
    average = (a + b + c) / 3

    # 3. Дискримінант: D = b² - 4ac
    discriminant = b ** 2 - 4 * a * c

    # 4. Гіпотенуза прямокутного трикутника з катетами a, b
    hypotenuse = math.sqrt(a ** 2 + b ** 2)

    # 5. Нерівність трикутника (логічні оператори and)
    is_triangle = (a > 0 and b > 0 and c > 0
                   and a + b > c and a + c > b and b + c > a)

    print(f"Сума квадратів: {sum_squares:.2f}")
    print(f"Середнє арифметичне: {average:.2f}")
    print(f"Дискримінант: {discriminant:.2f}")
    print(f"Гіпотенуза: {hypotenuse:.2f}")
    print(f"Утворюють трикутник: {'так' if is_triangle else 'ні'}")

    # Додатково: демонстрація операторів -, %, // та or
    print(f"Різниця a - b: {a - b:.2f}")
    if b != 0:
        print(f"Цілочисельне ділення a // b: {a // b:.2f}")
        print(f"Остача a % b: {a % b:.2f}")
    else:
        print("Ділення на b неможливе (b = 0)")
    has_negative = a < 0 or b < 0 or c < 0
    print(f"Є від'ємні числа: {'так' if has_negative else 'ні'}")


if __name__ == "__main__":
    main()
