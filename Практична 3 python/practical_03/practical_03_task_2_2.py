# practical_03_task_2_2.py

"""Декоратори класів."""

import functools
import inspect
import time


def auto_repr(cls):
    """Декоратор класу: додає __repr__ на основі __init__ параметрів."""
    # inspect.unwrap знаходить оригінальний __init__, навіть якщо його вже
    # обгорнув інший декоратор (наприклад, @frozen) — це дозволяє комбінувати
    code = inspect.unwrap(cls.__init__).__code__
    params = code.co_varnames[1:code.co_argcount]  # без self

    def __repr__(self):
        args = ", ".join(f"{p}={getattr(self, p, None)!r}" for p in params)
        return f"{type(self).__name__}({args})"

    cls.__repr__ = __repr__
    return cls


def frozen(cls):
    """Декоратор класу: забороняє зміну атрибутів після __init__.

    Після ініціалізації будь-яка спроба змінити атрибут
    викликає AttributeError.
    """
    original_init = cls.__init__

    @functools.wraps(original_init)
    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # object.__setattr__ обходить наш перевизначений __setattr__
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                f"Неможливо змінити '{name}': екземпляр {type(self).__name__} "
                f"заморожено"
            )
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                f"Неможливо видалити '{name}': екземпляр "
                f"{type(self).__name__} заморожено"
            )
        object.__delattr__(self, name)

    cls.__init__ = __init__
    cls.__setattr__ = __setattr__
    cls.__delattr__ = __delattr__
    return cls


def log_methods(cls):
    """Декоратор класу: логує виклики всіх публічних методів."""
    for name, attr in list(vars(cls).items()):
        if name.startswith("_") or not inspect.isfunction(attr):
            continue

        def make_wrapper(method, method_name):
            @functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                parts = [repr(a) for a in args]
                parts += [f"{k}={v!r}" for k, v in kwargs.items()]
                call = f"{cls.__name__}.{method_name}({', '.join(parts)})"
                start = time.perf_counter()
                try:
                    result = method(self, *args, **kwargs)
                except Exception as e:
                    print(f"[LOG] {call} → {type(e).__name__}: {e}")
                    raise
                elapsed = time.perf_counter() - start
                print(f"[LOG] {call} → {result} ({elapsed:.6f}с)")
                return result
            return wrapper

        setattr(cls, name, make_wrapper(attr, name))
    return cls


@auto_repr
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@frozen
class ImmutableConfig:
    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug


@log_methods
class MathService:
    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Ділення на нуль")
        return a / b


# Комбінація декораторів
@auto_repr
@frozen
class FrozenPoint:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


def main():
    print("=== @auto_repr ===")
    p = Point(3.0, 4.0)
    print(repr(p))  # Point(x=3.0, y=4.0)
    print(f"distance_to: {p.distance_to(Point(0, 0))}")

    print("\n=== @frozen ===")
    cfg = ImmutableConfig("localhost", 8080, debug=True)
    print(f"Config: {cfg.host}:{cfg.port}")
    try:
        cfg.host = "remote"
    except AttributeError as e:
        print(f"Очікувана помилка: {e}")

    print("\n=== @log_methods ===")
    svc = MathService()
    svc.add(10, 20)
    svc.multiply(3, 7)
    try:
        svc.divide(10, 0)
    except ValueError:
        pass

    print("\n=== Комбінація @auto_repr + @frozen ===")
    fp = FrozenPoint(1, 2)
    print(repr(fp))
    try:
        fp.x = 100
    except AttributeError as e:
        print(f"Очікувана помилка: {e}")


if __name__ == "__main__":
    main()
