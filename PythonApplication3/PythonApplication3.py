import time


print("=" * 60)
print("ЗАВДАННЯ 1. СПИСКИ")
print("=" * 60)

numbers = [10, 20, 30, 40, 50, 60, 70, 80]

print("1. Початковий список:")
print(numbers)

print("\n2. Звернення за додатним індексом:")
print("numbers[2] =", numbers[2])

print("\n3. Звернення за від'ємним індексом:")
print("numbers[-2] =", numbers[-2])

slice1 = numbers[1:5]
slice2 = numbers[:6:2]
slice3 = numbers[5:1:-1]

print("\n4. Зрізи:")
print("numbers[1:5]    =", slice1)
print("numbers[:6:2]   =", slice2)
print("numbers[5:1:-1] =", slice3)

print("\n5. Додавання елемента в кінець:")
numbers.append(90)
print(numbers)

print("\n6. Вставка елемента за індексом:")
numbers.insert(2, 25)
print(numbers)

print("\n7. Видалення елемента за індексом:")
del numbers[4]
print(numbers)

print("\nДовжина списку після мутацій:", len(numbers))



print("\n" + "=" * 60)
print("ЗАВДАННЯ 2. КОРТЕЖІ ТА РОЗПАКУВАННЯ")
print("=" * 60)


products = [
    (1, "Ноутбук", 3, 25000.0),
    (2, "Миша", 10, 800.0),
    (3, "Клавіатура", 5, 1500.0)
]


def get_product_info(product):
    product_id, name, quantity, price = product
    return product_id, name, quantity, price


def calculate_total(products):
    total = 0

    for product_id, name, quantity, price in products:
        total += quantity * price

    return total


print("Записи товарів:")

for product in products:
    product_id, name, quantity, price = get_product_info(product)

    print(
        "ID:", product_id,
        "| Назва:", name,
        "| Кількість:", quantity,
        "| Ціна:", price, "грн"
    )

total = calculate_total(products)

print("\nЗагальна вартість товарів:", round(total, 2), "грн")


print("\nСпроба змінити кортеж за індексом:")

try:
    products[0][1] = "Інший ноутбук"
except TypeError:
    print("Помилка: елементи кортежу не можна змінювати за індексом.")


print("\nКортеж із мутабельним вкладеним списком:")

student = ("Данило", "БІКСб 22540", [90, 85, 95])

print("До зміни:", student)

student[2].append(88)

print("Після зміни списку оцінок:", student)

print(
    "Сам кортеж залишається незмінним, "
    "але вкладений список є мутабельним."
)


print("\n" + "=" * 60)
print("ЗАВДАННЯ 3. СЛОВНИК ЧАСТОТ")
print("=" * 60)

text = """
Python простий і зручний.
Python використовується для програмування.
Програмування допомагає створювати програми.
"""

print("Вхідний текст:")
print(text)


punctuation = ".,!?;:-()\"'"

words = text.lower().split()

clean_words = []

for word in words:
    word = word.strip(punctuation)

    if word:
        clean_words.append(word)


frequency = {}

for word in clean_words:
    frequency[word] = frequency.get(word, 0) + 1


print("Частоти слів за алфавітом:")

for word in sorted(frequency):
    print(word, "->", frequency[word])


print("\nБезпечне отримання частоти:")

word = "кіт"
print(word, "->", frequency.get(word, 0))


print("\nПохідний словник: слова з частотою >= 2")

frequent_words = {
    word: count
    for word, count in frequency.items()
    if count >= 2
}

for word in sorted(frequent_words):
    print(word, "->", frequent_words[word])


print("\n" + "=" * 60)
print("ЗАВДАННЯ 4. МНОЖИНИ")
print("=" * 60)

list_a = ["PC01", "PC02", "PC03", "PC03", "PC04", "PC05"]
list_b = ["PC03", "PC04", "PC05", "PC06", "PC06", "PC07"]

set_a = set(list_a)
set_b = set(list_b)

print("Початкова колекція A:")
print(list_a)

print("Унікальні значення A:")
print(sorted(set_a))

print("\nПочаткова колекція B:")
print(list_b)

print("Унікальні значення B:")
print(sorted(set_b))


intersection = set_a & set_b
union = set_a | set_b
symmetric_difference = set_a ^ set_b

print("\nПеретин A і B:")
print(sorted(intersection))

print("\nОб'єднання A і B:")
print(sorted(union))

print("\nСиметрична різниця A і B:")
print(sorted(symmetric_difference))


subset_true = {"PC03", "PC04"} <= set_a
subset_false = {"PC03", "PC07"} <= set_a

print("\nПеревірка підмножини:")
print("{'PC03', 'PC04'} <= A ->", subset_true)
print("{'PC03', 'PC07'} <= A ->", subset_false)


print("\n" + "=" * 60)
print("ЗАВДАННЯ 5. АЛГОРИТМІЧНА СКЛАДНІСТЬ")
print("=" * 60)

sizes = [100, 1000, 10000]

print("\nПошук значення: список проти множини")
print("-" * 60)
print(f"{'n':<10}{'Список, мс':<20}{'Множина, мс':<20}")

for n in sizes:
    data_list = list(range(n))
    data_set = set(data_list)

    target = n - 1

    repetitions = 100

    start = time.perf_counter()

    for _ in range(repetitions):
        target in data_list

    list_time = (time.perf_counter() - start) / repetitions * 1000

    start = time.perf_counter()

    for _ in range(repetitions):
        target in data_set

    set_time = (time.perf_counter() - start) / repetitions * 1000

    print(f"{n:<10}{list_time:<20.6f}{set_time:<20.6f}")


print("\nПеревірка наявності ключа у словнику")
print("-" * 60)
print(f"{'n':<10}{'Час, мс':<20}")

for n in sizes:
    data_dict = {i: i for i in range(n)}

    target = n - 1
    repetitions = 100

    start = time.perf_counter()

    for _ in range(repetitions):
        target in data_dict

    dict_time = (time.perf_counter() - start) / repetitions * 1000

    print(f"{n:<10}{dict_time:<20.6f}")


print("\nПобудова унікальних значень")
print("-" * 60)
print(f"{'n':<10}{'Список, мс':<20}{'Множина, мс':<20}")

for n in sizes:
    data = list(range(n)) + list(range(n // 2))

    start = time.perf_counter()

    unique_list = []

    for value in data:
        if value not in unique_list:
            unique_list.append(value)

    list_unique_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()

    unique_set = set()

    for value in data:
        unique_set.add(value)

    set_unique_time = (time.perf_counter() - start) * 1000

    print(
        f"{n:<10}"
        f"{list_unique_time:<20.6f}"
        f"{set_unique_time:<20.6f}"
    )


