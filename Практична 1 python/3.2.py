# practical_01_task_3_2.py

"""Інтерактивний калькулятор на основі циклу while."""


def calculator():
    """Інтерактивний калькулятор з підтримкою +, -, *, /, //, %, **."""
    print("=== Калькулятор ===")
    print("Введіть вираз у форматі: число оператор число")
    print("Введіть 'quit' для виходу, 'history' для історії")

    history = []
    operators = ("+", "-", "*", "/", "//", "%", "**")

    while True:
        user_input = input("\n> ").strip()

        if user_input.lower() == "quit":
            print("До побачення!")
            break
        if user_input.lower() == "history":
            if history:
                for i, item in enumerate(history, 1):
                    print(f"{i}. {item}")
            else:
                print("Історія порожня")
            continue

        parts = user_input.split()
        if len(parts) != 3:
            print("Помилка: формат — число оператор число")
            continue

        left, op, right = parts
        try:
            x, y = float(left), float(right)
        except ValueError:
            print("Помилка: операнди мають бути числами")
            continue
        if op not in operators:
            print(f"Помилка: невідомий оператор '{op}'")
            continue

        if op in ("/", "//", "%") and y == 0:
            print("Помилка: ділення на нуль")
            continue

        if op == "+":
            result = x + y
        elif op == "-":
            result = x - y
        elif op == "*":
            result = x * y
        elif op == "/":
            result = x / y
        elif op == "//":
            result = x // y
        elif op == "%":
            result = x % y
        else:
            try:
                result = x ** y
            except (OverflowError, ZeroDivisionError):
                print("Помилка: неможливо обчислити степінь")
                continue
            if isinstance(result, complex):
                print("Помилка: результат комплексний")
                continue

        record = f"{x:g} {op} {y:g} = {result:g}"
        history.append(record)
        print(record)


if __name__ == "__main__":
    calculator()
