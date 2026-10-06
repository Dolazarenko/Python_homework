# practical_03_task_1_1.py

"""Система плагінів з автоматичною реєстрацією через метаклас."""

import hashlib
import re
from abc import abstractmethod


class PluginMeta(type):
    """Метаклас для автоматичної реєстрації та валідації плагінів.

    Кожен клас, створений з цим метакласом, автоматично додається
    до реєстру, якщо він визначає обов'язкові атрибути.
    """

    _registry: dict[str, type] = {}
    REQUIRED_ATTRS = ("name", "version")

    def __new__(mcs, cls_name: str, bases: tuple, namespace: dict):
        # Створюємо сам клас стандартним способом
        cls = super().__new__(mcs, cls_name, bases, namespace)

        # Базовий клас (без батьків) не реєструємо та не валідуємо
        if bases:
            # Перевірка обов'язкових атрибутів
            for attr in mcs.REQUIRED_ATTRS:
                if not hasattr(cls, attr):
                    raise TypeError(
                        f"Плагін '{cls_name}' повинен визначати "
                        f"обов'язковий атрибут '{attr}'"
                    )
            # Захист від дублікатів імен
            if cls.name in mcs._registry:
                raise ValueError(
                    f"Плагін з ім'ям '{cls.name}' уже зареєстровано "
                    f"({mcs._registry[cls.name].__name__})"
                )
            # Реєстрація: name -> class
            mcs._registry[cls.name] = cls
        return cls

    @classmethod
    def get_registry(mcs) -> dict[str, type]:
        """Повертає копію реєстру плагінів."""
        return dict(mcs._registry)

    @classmethod
    def create_plugin(mcs, plugin_name: str):
        """Фабричний метод: створює екземпляр плагіна за його name."""
        try:
            return mcs._registry[plugin_name]()
        except KeyError:
            raise ValueError(
                f"Невідомий плагін '{plugin_name}'. "
                f"Доступні: {list(mcs._registry)}"
            ) from None


class BasePlugin(metaclass=PluginMeta):
    """Базовий клас плагіна."""

    @abstractmethod
    def execute(self, data: str) -> str:
        """Обробити вхідні дані."""
        ...


class UpperPlugin(BasePlugin):
    """Перетворює текст у верхній регістр."""
    name = "upper"
    version = "1.0"

    def execute(self, data: str) -> str:
        return data.upper()


class ReversePlugin(BasePlugin):
    """Розвертає текст."""
    name = "reverse"
    version = "1.0"

    def execute(self, data: str) -> str:
        return data[::-1]


class CensorPlugin(BasePlugin):
    """Замінює задані слова на '***' (без урахування регістру)."""
    name = "censor"
    version = "1.1"

    def __init__(self, words: tuple[str, ...] = ("світ", "погано")):
        self.words = words

    def execute(self, data: str) -> str:
        for word in self.words:
            data = re.sub(re.escape(word), "***", data, flags=re.IGNORECASE)
        return data


# Динамічне створення класу через type() у тризначній формі
def _hash_execute(self, data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]


HashPlugin = type(
    "HashPlugin",
    (BasePlugin,),
    {"name": "hash", "version": "2.0", "execute": _hash_execute},
)


def main():
    print("Зареєстровані плагіни:")
    for name, cls in PluginMeta.get_registry().items():
        print(f"  {name} (v{cls.version}): {cls.__name__}")

    test_data = "Привіт Світ"
    print(f"\nВхідні дані: {test_data!r}")
    for name in PluginMeta.get_registry():
        plugin = PluginMeta.create_plugin(name)
        print(f"  {name}: {plugin.execute(test_data)}")

    # Клас без обов'язкових атрибутів -> TypeError
    print("\nКлас без обов'язкових атрибутів:")
    try:
        class BadPlugin(BasePlugin):
            name = "bad"  # відсутній атрибут version

            def execute(self, data: str) -> str:
                return data
    except TypeError as e:
        print(f"  Очікувана помилка: {e}")

    print(f"  'bad' у реєстрі: {'bad' in PluginMeta.get_registry()}")

    # Невідомий плагін
    try:
        PluginMeta.create_plugin("unknown")
    except ValueError as e:
        print(f"  Очікувана помилка: {e}")


if __name__ == "__main__":
    main()
