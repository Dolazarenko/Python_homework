
"""
Консольна програма: математичні задачі, типи й структури даних,
ітератори та генератори.

Запуск:  python math_console_app.py
"""

import math


def read_int(prompt, min_value=None):
    """Зчитує ціле число з перевіркою коректності."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("  ! Потрібно ввести ціле число.")
            continue
        if min_value is not None and value < min_value:
            print(f"  ! Число має бути не менше {min_value}.")
            continue
        return value


def read_float(prompt, positive=True):
    """Зчитує дійсне число (за потреби — строго додатне)."""
    while True:
        text = input(prompt).strip().replace(",", ".")
        try:
            value = float(text)
        except ValueError:
            print("  ! Потрібно ввести число.")
            continue
        if positive and value <= 0:
            print("  ! Число має бути більшим за нуль.")
            continue
        return value


def title(text):
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)


def factorial_for(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def factorial_while(n):
    result, i = 1, n
    while i > 1:
        result *= i
        i -= 1
    return result


def factorial_recursive(n):
    return 1 if n <= 1 else n * factorial_recursive(n - 1)


def task_factorial():
    title("ФАКТОРІАЛ ЧИСЛА")
    n = read_int("Введіть n (n >= 0): ", min_value=0)
    print(f"  цикл for       : {n}! = {factorial_for(n)}")
    print(f"  цикл while     : {n}! = {factorial_while(n)}")
    if n <= 900:  # обмеження глибини рекурсії
        print(f"  рекурсія       : {n}! = {factorial_recursive(n)}")
    else:
        print("  рекурсія       : пропущено (занадто велике n)")
    print(f"  перевірка math : {n}! = {math.factorial(n)}")



def circle_calc():
    r = read_float("  Радіус кола: ")
    return {"Площа": math.pi * r ** 2, "Довжина кола": 2 * math.pi * r}


def rectangle_calc():
    a = read_float("  Сторона a: ")
    b = read_float("  Сторона b: ")
    return {"Площа": a * b, "Периметр": 2 * (a + b), "Діагональ": math.hypot(a, b)}


def triangle_calc():
    while True:
        a = read_float("  Сторона a: ")
        b = read_float("  Сторона b: ")
        c = read_float("  Сторона c: ")
        if a + b > c and a + c > b and b + c > a:
            break
        print("  ! Трикутник з такими сторонами не існує, спробуйте ще раз.")
    p = (a + b + c) / 2
    area = math.sqrt(p * (p - a) * (p - b) * (p - c))  
    if a == b == c:
        kind = "рівносторонній"
    elif a == b or b == c or a == c:
        kind = "рівнобедрений"
    elif math.isclose(max(a, b, c) ** 2, a * a + b * b + c * c - max(a, b, c) ** 2):
        kind = "прямокутний"
    else:
        kind = "різносторонній"
    return {"Площа (Герон)": area, "Периметр": 2 * p, "Тип": kind}


def task_geometry():
    title("ГЕОМЕТРИЧНІ ФІГУРИ")
   
    figures = {
        "1": ("Коло", circle_calc),
        "2": ("Прямокутник", rectangle_calc),
        "3": ("Трикутник", triangle_calc),
    }
    for key, (name, _) in figures.items():
        print(f"  {key}. {name}")
    choice = input("Оберіть фігуру: ").strip()
    if choice not in figures:
        print("  ! Невірний вибір.")
        return
    name, func = figures[choice]
    print(f"\n{name}:")
    for label, value in func().items():
        if isinstance(value, float):
            print(f"  {label}: {value:.4f}")
        else:
            print(f"  {label}: {value}")


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for d in range(3, int(math.sqrt(n)) + 1, 2):
        if n % d == 0:
            return False
    return True


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def task_numbers():
    title("ЧИСЛОВІ ЗАДАЧІ")
    n = read_int("Введіть натуральне число n: ", min_value=1)

    # Парність
    parity = "парне" if n % 2 == 0 else "непарне"
    print(f"  {n} — {parity} число")

    # Простота
    print(f"  {n} — {'просте' if is_prime(n) else 'складене (або 1)'} число")

    # Сума цифр
    digits_sum, tmp = 0, n
    while tmp > 0:
        digits_sum += tmp % 10
        tmp //= 10
    print(f"  Сума цифр: {digits_sum}")

    # Дільники
    divisors = [d for d in range(1, n + 1) if n % d == 0]
    print(f"  Дільники: {divisors}")

    # Двійкова/вісімкова/шістнадцяткова системи
    print(f"  bin: {bin(n)}, oct: {oct(n)}, hex: {hex(n)}")

    # НСД та НСК з другим числом
    m = read_int("Введіть друге натуральне число m: ", min_value=1)
    g = gcd(n, m)
    print(f"  НСД({n}, {m}) = {g}, НСК({n}, {m}) = {n * m // g}")

    # FizzBuzz (приклад if/elif/else у циклі)
    print("  FizzBuzz від 1 до 15:", end=" ")
    for i in range(1, 16):
        if i % 15 == 0:
            print("FizzBuzz", end=" ")
        elif i % 3 == 0:
            print("Fizz", end=" ")
        elif i % 5 == 0:
            print("Buzz", end=" ")
        else:
            print(i, end=" ")
    print()



def task_data_types():
    title("ТИПИ ТА СТРУКТУРИ ДАНИХ")

    print("\n--- Базові типи ---")
    samples = [42, 3.14, 2 + 3j, "Привіт", True, None]
    for item in samples:
        print(f"  {item!r:<10} -> {type(item).__name__}")

    print("\n--- Список (list) — змінюваний ---")
    numbers = [5, 3, 8, 1, 9, 2]
    print("  Початковий список :", numbers)
    numbers.append(7)
    numbers.insert(0, 10)
    numbers.remove(8)
    print("  Після змін        :", numbers)
    print("  Відсортований     :", sorted(numbers))
    print("  Зворотний порядок :", numbers[::-1])
    print(f"  min={min(numbers)}, max={max(numbers)}, "
          f"sum={sum(numbers)}, avg={sum(numbers) / len(numbers):.2f}")
    squares = [x ** 2 for x in numbers if x % 2 == 0]
    print("  Квадрати парних   :", squares)

    print("\n--- Кортеж (tuple) — незмінюваний ---")
    point = (3, 4)
    x, y = point  # розпакування
    print(f"  Точка {point}: x={x}, y={y}, відстань до O = {math.hypot(x, y)}")
    try:
        point[0] = 10
    except TypeError as err:
        print("  Спроба змінити кортеж ->", err)
    print("  Заміна змінних (a, b = b, a):", end=" ")
    a, b = 1, 2
    a, b = b, a
    print(a, b)

    print("\n--- Словник (dict) ---")
    student = {"ім'я": "Олена", "вік": 19, "оцінки": [90, 85, 100]}
    student["група"] = "КН-21"
    print("  Словник:", student)
    avg = sum(student["оцінки"]) / len(student["оцінки"])
    print(f"  Середня оцінка: {avg:.1f}")
    for key, value in student.items():
        print(f"    {key:<8}: {value}")


    text = "математика"
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    print(f"  Частота літер у слові '{text}':", freq)

    print("\n--- Множина (set) ---")
    s1, s2 = {1, 2, 3, 4, 5}, {4, 5, 6, 7}
    print("  s1 | s2 =", s1 | s2)
    print("  s1 & s2 =", s1 & s2)
    print("  s1 - s2 =", s1 - s2)
    print("  s1 ^ s2 =", s1 ^ s2)
    print("  Унікальні з [1,1,2,3,3]:", set([1, 1, 2, 3, 3]))


class Countdown:
    """Ітератор зворотного відліку: реалізує __iter__ та __next__."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class FibonacciIterator:
    """Ітератор перших `count` чисел Фібоначчі."""

    def __init__(self, count):
        self.count = count
        self.index = 0
        self.a, self.b = 0, 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= self.count:
            raise StopIteration
        self.index += 1
        value = self.a
        self.a, self.b = self.b, self.a + self.b
        return value


class NumberCollection:
    """Власна колекція: iterable, що щоразу повертає новий ітератор."""

    def __init__(self, *items):
        self.items = list(items)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


def fibonacci_gen(limit):
    """Генератор чисел Фібоначчі, що не перевищують limit."""
    a, b = 0, 1
    while a <= limit:
        yield a
        a, b = b, a + b


def primes_gen():
    """Нескінченний генератор простих чисел."""
    n = 2
    while True:
        if is_prime(n):
            yield n
        n += 1


def take(iterable, n):
    """Бере перші n елементів із будь-якого ітератора."""
    result = []
    for item in iterable:
        if len(result) >= n:
            break
        result.append(item)
    return result


def running_sum(iterable):
    """Генератор часткових сум."""
    total = 0
    for x in iterable:
        total += x
        yield total


def task_iterators():
    title("ІТЕРАТОРИ ТА ГЕНЕРАТОРИ")

    print("\n--- Вбудовані iter() / next() ---")
    it = iter(["a", "b", "c"])
    print("  next:", next(it), next(it), next(it))
    try:
        next(it)
    except StopIteration:
        print("  Далі елементів немає -> StopIteration")

    print("\n--- Ітератор-клас Countdown(5) ---")
    print("  ", list(Countdown(5)))

    print("\n--- Ітератор-клас FibonacciIterator(10) ---")
    print("  ", list(FibonacciIterator(10)))

    print("\n--- Власна колекція NumberCollection ---")
    coll = NumberCollection(10, 20, 30)
    print(f"  Елементів: {len(coll)}; обхід:", end=" ")
    for value in coll:
        print(value, end=" ")
    print()

    print("\n--- Генератор fibonacci_gen(100) ---")
    print("  ", list(fibonacci_gen(100)))

    print("\n--- Нескінченний генератор простих чисел ---")
    print("  Перші 10 простих:", take(primes_gen(), 10))

    print("\n--- Конвеєр генераторів ---")
    evens = (x for x in range(1, 21) if x % 2 == 0)  # генераторний вираз
    print("  Часткові суми парних 1..20:", list(running_sum(evens)))

    print("\n--- Ітерація по словнику та з enumerate / zip ---")
    prices = {"яблука": 25.5, "груші": 32.0, "сливи": 18.75}
    for i, (name, price) in enumerate(prices.items(), start=1):
        print(f"  {i}. {name:<7} {price:>6.2f} грн")
    names = ["Іра", "Петро", "Оксана"]
    scores = (88, 92, 79)
    print("  zip:", list(zip(names, scores)))

    print("\n--- Економія пам'яті: список vs генератор ---")
    import sys
    as_list = [x * x for x in range(100_000)]
    as_gen = (x * x for x in range(100_000))
    print(f"  list: {sys.getsizeof(as_list)} байт")
    print(f"  gen : {sys.getsizeof(as_gen)} байт")
    print(f"  Сума квадратів (через генератор): {sum(as_gen)}")



def run_all():
    """Короткий автоматичний показ без введення з клавіатури."""
    title("АВТОДЕМОНСТРАЦІЯ")
    print("  10! =", factorial_for(10))
    print("  Прості до 50:", [n for n in range(50) if is_prime(n)])
    print("  Fibonacci <= 100:", list(fibonacci_gen(100)))
    print("  Countdown(3):", list(Countdown(3)))
    print("  Перші 5 простих:", take(primes_gen(), 5))


def main():
    actions = {
        "1": ("Факторіал числа", task_factorial),
        "2": ("Геометричні фігури", task_geometry),
        "3": ("Числові задачі", task_numbers),
        "4": ("Типи та структури даних", task_data_types),
        "5": ("Ітератори та генератори", task_iterators),
        "6": ("Швидка демонстрація", run_all),
        "0": ("Вихід", None),
    }
    while True:
        title("МАТЕМАТИЧНИЙ КОНСОЛЬНИЙ ДОДАТОК")
        for key, (name, _) in actions.items():
            print(f"  {key}. {name}")
        choice = input("\nВаш вибір: ").strip()
        if choice == "0":
            print("До побачення!")
            break
        if choice in actions:
            try:
                actions[choice][1]()
            except (KeyboardInterrupt, EOFError):
                print("\n  Операцію перервано.")
        else:
            print("  ! Невідомий пункт меню.")


if __name__ == "__main__":
    main()