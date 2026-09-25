"""Демонстраційний скрипт: `from shop_system import *` (Завдання 3).

Використання `from module import *` заборонене в робочому коді пакета,
але тут воно навмисно застосоване для перевірки того, що імпортуються
лише імена, перелічені в `shop_system.__all__`.

Запуск: python demo_star_import.py
"""

from shop_system import *  # noqa: F401,F403  (навмисно, лише для демонстрації)

if __name__ == "__main__":
    imported_names = sorted(name for name in dir() if not name.startswith("_") and name != "annotations")
    print("Імена, імпортовані через `from shop_system import *`:")
    print(imported_names)

    import shop_system

    print(f"\nОчікувані імена з shop_system.__all__: {sorted(shop_system.__all__)}")
    assert imported_names == sorted(shop_system.__all__), "Star-import імпортував зайві імена!"
    print("Підтверджено: імпортовано рівно ті імена, що вказані в __all__.")
