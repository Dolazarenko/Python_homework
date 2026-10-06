# practical_01_task_1_2.py

"""Конвертор типів та форматоване виведення."""


def main():
    raw_input = input("Введіть число: ")

    # --- Перетворення типів з обробкою помилок ---
    try:
        as_float = float(raw_input)
        as_int = int(as_float)  # int("3.5") дало б помилку, тому через float
        as_bool = bool(as_float)
        as_str = str(as_float)
        print(f"int:   {as_int!r:>10}  тип: {type(as_int).__name__}")
        print(f"float: {as_float!r:>10}  тип: {type(as_float).__name__}")
        print(f"bool:  {as_bool!r:>10}  тип: {type(as_bool).__name__}")
        print(f"str:   {as_str!r:>10}  тип: {type(as_str).__name__}")
        print(f"as_int є int? {isinstance(as_int, int)}; "
              f"as_float є int? {isinstance(as_float, int)}")
    except ValueError:
        print(f"Помилка: '{raw_input}' не є числом.")
    except OverflowError:
        print("Помилка: число занадто велике для перетворення в int.")

    # --- Ім'я та вік, f-рядки зі специфікаторами ---
    name = input("Введіть ім'я: ")
    try:
        age = int(input("Введіть вік: "))
    except ValueError:
        print("Помилка: вік має бути цілим числом.")
        age = 0

    print(f"|{name:<12}|{name:^12}|{name:>12}|")   # вирівнювання
    print(f"Вік (з нулями): {age:05d}")              # доповнення нулями
    print(f"Вік у float: {age:.2f}")                 # кількість знаків
    print(f"Вік у двійковому вигляді: {age:b}")
    print(f"Привіт, {name}! Тобі {age} р.")

    # --- id(), len(), range() ---
    numbers = list(range(0, 20, 3))
    print(f"Список: {numbers}")
    print(f"Довжина списку: {len(numbers)}")
    print(f"id списку: {id(numbers)}")
    print(f"Довжина імені: {len(name)}")
    print(f"Сума: {sum(numbers)}, мін: {min(numbers)}, макс: {max(numbers)}")


if __name__ == "__main__":
    main()
