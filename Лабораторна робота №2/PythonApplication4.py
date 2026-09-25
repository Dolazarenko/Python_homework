# ============================================================
# ЗАВДАННЯ 1
# Класова ієрархія з наслідуванням та поліморфізмом
# Предметна область: транспортні засоби
# ============================================================


class Vehicle:
    def __init__(self, brand, max_speed):
        self.brand = brand
        self.max_speed = max_speed

    def move(self):
        return f"{self.brand} рухається зі швидкістю до {self.max_speed} км/год"

    def __str__(self):
        return f"{self.brand}, максимальна швидкість: {self.max_speed} км/год"


class Car(Vehicle):
    def __init__(self, brand, max_speed, doors):
        super().__init__(brand, max_speed)
        self.doors = doors

    def move(self):
        return f"Автомобіль {self.brand} рухається дорогою зі швидкістю {self.max_speed} км/год"


class Motorcycle(Vehicle):
    def __init__(self, brand, max_speed, engine_volume):
        super().__init__(brand, max_speed)
        self.engine_volume = engine_volume

    def move(self):
        return f"Мотоцикл {self.brand} рухається зі швидкістю {self.max_speed} км/год"


class Truck(Vehicle):
    def __init__(self, brand, max_speed, load_capacity):
        super().__init__(brand, max_speed)
        self.load_capacity = load_capacity

    def move(self):
        return f"Вантажівка {self.brand} перевозить до {self.load_capacity} тонн вантажу"


vehicles = [
    Car("Toyota", 200, 4),
    Motorcycle("Honda", 180, 600),
    Truck("Volvo", 120, 20)
]

print("ЗАВДАННЯ 1")
print("Класова ієрархія та поліморфізм\n")

print("Поліморфний обхід:")

for vehicle in vehicles:
    print(vehicle.move())

print("\nПеревірка типів:")

print("Car є Vehicle:", isinstance(vehicles[0], Vehicle))
print("Motorcycle є Motorcycle:", isinstance(vehicles[1], Motorcycle))
print("Car є підкласом Vehicle:", issubclass(Car, Vehicle))
print("Truck є підкласом Vehicle:", issubclass(Truck, Vehicle))

print("\nРядкове представлення:")

for vehicle in vehicles:
    print(vehicle)


# ============================================================
# ЗАВДАННЯ 2
# Інкапсуляція, property та контроль доступу
# Предметна область: банківський рахунок
# ============================================================


class BankAccount:
    def __init__(self, owner, balance, account_type):
        self.owner = owner
        self.__balance = 0
        self._account_type = account_type
        self.balance = balance

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс повинен бути числом")

        if value < 0:
            raise ValueError("Баланс не може бути від'ємним")

        self.__balance = value

    @property
    def is_positive(self):
        return self.__balance > 0

    def __str__(self):
        return f"Власник: {self.owner}, баланс: {self.balance} грн"


account = BankAccount("Данило", 5000, "Основний")

print("\n\nЗАВДАННЯ 2")
print("Інкапсуляція та property\n")

print("Створений рахунок:")
print(account)

print("\nОбчислювана властивість:")
print("Баланс додатний:", account.is_positive)

print("\nЗміна балансу:")
account.balance = 7500
print("Новий баланс:", account.balance)

print("\nСпроба встановити від'ємний баланс:")

try:
    account.balance = -100
except ValueError as error:
    print("Помилка:", error)

print("\nСпроба встановити текст замість числа:")

try:
    account.balance = "1000"
except TypeError as error:
    print("Помилка:", error)

print("\nПрямий доступ до приватного атрибута:")

try:
    print(account.__balance)
except AttributeError as error:
    print("Помилка:", error)

print("\nДоступ через name mangling:")
print(account._BankAccount__balance)

print("\nЗахищений атрибут:")
print(account._account_type)


# ============================================================
# ЗАВДАННЯ 3
# Магічні методи та перевантаження операторів
# Предметна область: часовий інтервал
# ============================================================


class TimeInterval:
    def __init__(self, minutes):
        if not isinstance(minutes, int):
            raise TypeError("Тривалість повинна бути цілим числом")

        self.minutes = minutes

    def __str__(self):
        hours = abs(self.minutes) // 60
        minutes = abs(self.minutes) % 60

        sign = "-" if self.minutes < 0 else ""

        return f"{sign}{hours} год {minutes} хв"

    def __repr__(self):
        return f"TimeInterval({self.minutes})"

    def __add__(self, other):
        if not isinstance(other, TimeInterval):
            return NotImplemented

        return TimeInterval(self.minutes + other.minutes)

    def __sub__(self, other):
        if not isinstance(other, TimeInterval):
            return NotImplemented

        return TimeInterval(self.minutes - other.minutes)

    def __eq__(self, other):
        if not isinstance(other, TimeInterval):
            return False

        return self.minutes == other.minutes

    def __lt__(self, other):
        if not isinstance(other, TimeInterval):
            return NotImplemented

        return self.minutes < other.minutes

    def __len__(self):
        return abs(self.minutes)

    def __abs__(self):
        return TimeInterval(abs(self.minutes))


first = TimeInterval(90)
second = TimeInterval(45)
negative = TimeInterval(-150)

print("\n\nЗАВДАННЯ 3")
print("Магічні методи та перевантаження операторів\n")

print("str:")
print(str(first))

print("\nrepr:")
print(repr(first))

print("\nДодавання:")
print(first + second)

print("\nВіднімання:")
print(first - second)

print("\nПорівняння:")
print("first == second:", first == second)
print("first < second:", first < second)

print("\nДовжина:")
print(len(first))

print("\nМодуль:")
print(abs(negative))


# ============================================================
# ЗАВДАННЯ 4
# Абстрактні класи та композиція
# Предметна область: система обробки платежів
# ============================================================


from abc import ABC, abstractmethod


class PaymentProcessor(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def validate(self, amount):
        pass

    @abstractmethod
    def pay(self, amount):
        pass

    def describe(self):
        return f"Процесор платежів: {self.name}"


class CardProcessor(PaymentProcessor):

    @property
    def name(self):
        return "Банківська картка"

    def validate(self, amount):
        return amount > 0

    def pay(self, amount):
        if not self.validate(amount):
            return "Некоректна сума платежу"

        return f"Оплачено {amount} грн банківською карткою"


class CryptoProcessor(PaymentProcessor):

    @property
    def name(self):
        return "Криптовалюта"

    def validate(self, amount):
        return amount > 10

    def pay(self, amount):
        if not self.validate(amount):
            return "Мінімальна сума криптоплатежу: 10 грн"

        return f"Оплачено {amount} грн криптовалютою"


class Logger:
    def log(self, message):
        print(f"[LOG] {message}")


class PaymentService:
    def __init__(self, processor, logger):
        self.processor = processor
        self.logger = logger

    def process_payment(self, amount):
        result = self.processor.pay(amount)
        self.logger.log(result)
        return result


print("\n\nЗАВДАННЯ 4")
print("Абстрактні класи та композиція\n")

print("Спроба створення абстрактного класу:")

try:
    processor = PaymentProcessor()
except TypeError as error:
    print("Помилка:", error)


card_processor = CardProcessor()
crypto_processor = CryptoProcessor()

logger = Logger()

card_service = PaymentService(card_processor, logger)
crypto_service = PaymentService(crypto_processor, logger)

print("\nІнформація про процесори:")

print(card_processor.describe())
print(crypto_processor.describe())

print("\nПоліморфний виклик:")

processors = [
    card_processor,
    crypto_processor
]

for processor in processors:
    print(processor.name)
    print(processor.pay(500))

print("\nРобота композиції:")

card_service.process_payment(1000)
crypto_service.process_payment(500)


# ============================================================
# ЗАВДАННЯ 5
# Паттерн проектування Strategy
# Предметна область: розрахунок вартості доставки
# ============================================================


class DeliveryStrategy(ABC):

    @abstractmethod
    def calculate(self, distance):
        pass

    @abstractmethod
    def description(self):
        pass


class CourierDelivery(DeliveryStrategy):

    def calculate(self, distance):
        return 80 + distance * 12

    def description(self):
        return "Кур'єрська доставка"


class PostalDelivery(DeliveryStrategy):

    def calculate(self, distance):
        return 50 + distance * 7

    def description(self):
        return "Поштове відправлення"


class PickupDelivery(DeliveryStrategy):

    def calculate(self, distance):
        return 0

    def description(self):
        return "Самовивіз"


class Order:
    def __init__(self, number, total, strategy):
        self.number = number
        self.total = total
        self.strategy = strategy

    def calculate_total(self, distance):
        delivery_price = self.strategy.calculate(distance)
        return self.total + delivery_price

    def show_information(self, distance):
        delivery_price = self.strategy.calculate(distance)

        print(f"Замовлення №{self.number}")
        print(f"Спосіб доставки: {self.strategy.description()}")
        print(f"Вартість товарів: {self.total} грн")
        print(f"Вартість доставки: {delivery_price} грн")
        print(f"Загальна вартість: {self.calculate_total(distance)} грн")


distance = 10

courier_order = Order(
    101,
    1200,
    CourierDelivery()
)

postal_order = Order(
    102,
    1200,
    PostalDelivery()
)

pickup_order = Order(
    103,
    1200,
    PickupDelivery()
)

print("\n\nЗАВДАННЯ 5")
print("Паттерн Strategy\n")

courier_order.show_information(distance)

print()

postal_order.show_information(distance)

print()

pickup_order.show_information(distance)


class ExpressDelivery(DeliveryStrategy):

    def calculate(self, distance):
        return 150 + distance * 20

    def description(self):
        return "Експрес-доставка"


print("\nНова стратегія:")

express_order = Order(
    104,
    1200,
    ExpressDelivery()
)

express_order.show_information(distance)