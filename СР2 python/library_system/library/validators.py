"""Валідатори вхідних даних та декоратор @validate для перевірки аргументів."""
from __future__ import annotations

import functools
import inspect
import re
from datetime import date
from typing import Any, Callable

from .exceptions import ValidationError

Validator = Callable[[str, Any], None]

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_MIN_YEAR = 1450  # рік появи друкарського верстата Гутенберга


def non_empty_str(field: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"'{field}' має бути непорожнім рядком, отримано {value!r}")


def year_in_range(field: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"'{field}' має бути цілим числом, отримано {value!r}")
    upper = date.today().year
    if not _MIN_YEAR <= value <= upper:
        raise ValidationError(f"'{field}' має бути в межах {_MIN_YEAR}–{upper}, отримано {value}")


def valid_email(field: str, value: Any) -> None:
    if not isinstance(value, str) or not _EMAIL_RE.match(value.strip()):
        raise ValidationError(f"'{field}' має некоректний формат e-mail: {value!r}")


def normalize_isbn(value: str) -> str:
    return value.replace("-", "").replace(" ", "").upper()


def isbn13_check_digit(first12: str) -> str:
    total = sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(first12))
    return str((10 - total % 10) % 10)


def _isbn10_ok(code: str) -> bool:
    if not re.fullmatch(r"\d{9}[\dX]", code):
        return False
    total = sum((10 - i) * (10 if ch == "X" else int(ch)) for i, ch in enumerate(code))
    return total % 11 == 0


def _isbn13_ok(code: str) -> bool:
    if not re.fullmatch(r"\d{13}", code):
        return False
    return isbn13_check_digit(code[:12]) == code[12]


def valid_isbn(field: str, value: Any) -> None:
    """Перевіряє ISBN-10 або ISBN-13 (формат і контрольну суму)."""
    if not isinstance(value, str):
        raise ValidationError(f"'{field}' має бути рядком, отримано {type(value).__name__}")
    code = normalize_isbn(value)
    ok = (len(code) == 10 and _isbn10_ok(code)) or (len(code) == 13 and _isbn13_ok(code))
    if not ok:
        raise ValidationError(f"'{field}' — некоректний ISBN (формат або контрольна сума): {value!r}")


def make_isbn13(body9: str) -> str:
    """Будує коректний ISBN-13 з 9 цифр тіла. Зручно для тестів і демонстрації."""
    first12 = "978" + body9
    return first12 + isbn13_check_digit(first12)


def optional(check: Validator) -> Validator:
    """Робить перевірку необов'язковою: None приймається без перевірки."""

    def _check(field: str, value: Any) -> None:
        if value is not None:
            check(field, value)

    return _check


def validate(**rules: Validator) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор: перед викликом перевіряє зазначені аргументи функції або методу.

    Приклад:
        @validate(title=non_empty_str, year=year_in_range)
        def __init__(self, title, year): ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(*args, **kwargs)  # зайві/відсутні аргументи -> TypeError
            bound.apply_defaults()
            for name, check in rules.items():
                check(name, bound.arguments[name])
            return func(*args, **kwargs)

        return wrapper

    return decorator
