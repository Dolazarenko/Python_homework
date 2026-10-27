"""Доменні моделі бібліотеки. Усі моделі створюються через метаклас TrackedMeta."""
from __future__ import annotations

from .exceptions import ValidationError
from .logging_meta import TrackedMeta
from .validators import (
    non_empty_str,
    normalize_isbn,
    optional,
    valid_email,
    valid_isbn,
    validate,
    year_in_range,
)


class Entity(metaclass=TrackedMeta):
    """Базова сутність з ідентифікатором, який призначає Repository."""

    def __init__(self) -> None:
        self.id: int | None = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id})"


class Author(Entity):
    @validate(name=non_empty_str, birth_year=optional(year_in_range))
    def __init__(self, name: str, birth_year: int | None = None) -> None:
        super().__init__()
        self.name = name.strip()
        self.birth_year = birth_year


class Book(Entity):
    @validate(title=non_empty_str, isbn=valid_isbn, year=year_in_range)
    def __init__(self, title: str, isbn: str, year: int, author: Author) -> None:
        super().__init__()
        if not isinstance(author, Author):
            raise ValidationError("'author' має бути екземпляром Author")
        self.title = title.strip()
        self.isbn = normalize_isbn(isbn)
        self.year = year
        self.author = author
        self.borrowed_by: int | None = None  # id читача або None, якщо книга вільна

    @property
    def is_available(self) -> bool:
        return self.borrowed_by is None


class Reader(Entity):
    @validate(name=non_empty_str, email=valid_email)
    def __init__(self, name: str, email: str) -> None:
        super().__init__()
        self.name = name.strip()
        self.email = email.strip().lower()
        self.borrowed_ids: set[int] = set()
