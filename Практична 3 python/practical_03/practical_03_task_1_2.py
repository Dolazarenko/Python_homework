# practical_03_task_1_2.py

"""Типізовані дескриптори та __init_subclass__ для системи конфігурації."""


class ValidatedField:
    """Дескриптор із валідацією типу та діапазону значень.

    Використовує __set_name__ для автоматичного визначення імені атрибута.
    """

    def __init__(self, expected_type: type, min_value=None, max_value=None):
        self.expected_type = expected_type
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        # Ім'я поля та ім'я атрибута для приватного зберігання
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return getattr(obj, self.private_name)
        except AttributeError:
            raise AttributeError(f"Поле '{self.name}' ще не встановлено") from None

    def __set__(self, obj, value):
        # bool є підкласом int, тому явно забороняємо його для int-полів
        if not isinstance(value, self.expected_type) or (
            isinstance(value, bool) and self.expected_type is not bool
        ):
            raise TypeError(
                f"Поле '{self.name}' очікує {self.expected_type.__name__}, "
                f"отримано {type(value).__name__} ({value!r})"
            )
        if self.min_value is not None and value < self.min_value:
            raise ValueError(
                f"Поле '{self.name}': значення {value} менше за мінімум "
                f"{self.min_value}"
            )
        if self.max_value is not None and value > self.max_value:
            raise ValueError(
                f"Поле '{self.name}': значення {value} більше за максимум "
                f"{self.max_value}"
            )
        setattr(obj, self.private_name, value)


class ConfigSection:
    """Базовий клас секції конфігурації з автоматичною реєстрацією."""

    _sections: dict[str, type] = {}

    def __init_subclass__(cls, section_name: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        # Якщо ім'я не вказано — беремо ім'я класу в нижньому регістрі
        ConfigSection._sections[section_name or cls.__name__.lower()] = cls

    @classmethod
    def get_section(cls, name: str):
        """Повертає клас секції за іменем."""
        try:
            return ConfigSection._sections[name]
        except KeyError:
            raise KeyError(
                f"Секцію '{name}' не знайдено. "
                f"Доступні: {cls.list_sections()}"
            ) from None

    @classmethod
    def list_sections(cls) -> list[str]:
        """Повертає список усіх зареєстрованих секцій."""
        return list(ConfigSection._sections)


class DatabaseConfig(ConfigSection, section_name="database"):
    host = ValidatedField(str)
    port = ValidatedField(int, min_value=1, max_value=65535)
    max_connections = ValidatedField(int, min_value=1, max_value=1000)

    def __init__(self, host: str, port: int, max_connections: int):
        self.host = host
        self.port = port
        self.max_connections = max_connections

    def __repr__(self):
        return (f"DatabaseConfig(host={self.host!r}, port={self.port}, "
                f"max_connections={self.max_connections})")


class LoggingConfig(ConfigSection, section_name="logging"):
    level = ValidatedField(str)
    max_file_size_mb = ValidatedField(int, min_value=1, max_value=1024)

    def __init__(self, level: str, max_file_size_mb: int):
        self.level = level
        self.max_file_size_mb = max_file_size_mb

    def __repr__(self):
        return (f"LoggingConfig(level={self.level!r}, "
                f"max_file_size_mb={self.max_file_size_mb})")


def main():
    print(f"Зареєстровані секції: {ConfigSection.list_sections()}")
    print(f"get_section('database') -> {ConfigSection.get_section('database').__name__}")

    db = DatabaseConfig("localhost", 5432, 100)
    print(f"Створено: {db}")
    log_cfg = LoggingConfig("INFO", 50)
    print(f"Створено: {log_cfg}")

    # Невірний тип
    try:
        db.port = "5432"
    except TypeError as e:
        print(f"Очікувана помилка типу: {e}")

    # Значення за межами діапазону
    try:
        db.port = 70000
    except ValueError as e:
        print(f"Очікувана помилка діапазону: {e}")

    try:
        db.max_connections = 0
    except ValueError as e:
        print(f"Очікувана помилка діапазону: {e}")

    # Після невдалих спроб значення не змінилось
    print(f"Port після помилок: {db.port}")

    # Доступ до дескриптора через клас
    print(f"DatabaseConfig.port -> {type(DatabaseConfig.port).__name__}")


if __name__ == "__main__":
    main()
