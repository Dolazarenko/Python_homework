"""Патерн Factory: створення книг із зовнішніх записів (словників, рядків CSV/JSON)."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .exceptions import ValidationError
from .models import Author, Book


class BookFactory:
    REQUIRED_FIELDS = ("title", "isbn", "year")

    @classmethod
    def from_record(cls, record: Mapping[str, Any], author: Author) -> Book:
        """Створює Book із запису. Перетворює рік з рядка, перевіряє наявність полів."""
        if not isinstance(record, Mapping):
            raise ValidationError(f"Запис має бути словником, отримано {type(record).__name__}")
        missing = [field for field in cls.REQUIRED_FIELDS if field not in record]
        if missing:
            raise ValidationError(f"Відсутні обов'язкові поля: {', '.join(missing)}")
        year = _to_int(record["year"], "year")
        return Book(record["title"], record["isbn"], year, author)


def _to_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValidationError(f"Поле '{field}' має бути цілим числом, отримано {value!r}")
    try:
        return int(value)
    except ValueError:
        raise ValidationError(f"Поле '{field}' має бути цілим числом, отримано {value!r}") from None
