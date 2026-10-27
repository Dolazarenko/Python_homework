"""Фасад LibraryService: єдина точка входу до бізнес-логіки бібліотеки."""
from __future__ import annotations

import threading
from collections.abc import Mapping
from typing import Any

from .exceptions import (
    BookUnavailableError,
    DuplicateError,
    LoanLimitError,
    NotBorrowedError,
    ValidationError,
)
from .factories import BookFactory
from .logging_meta import log_call
from .models import Author, Book, Reader
from .patterns import EventBus, LoanPolicy, StandardPolicy
from .repository import Repository
from .validators import non_empty_str, valid_email


class LibraryService:
    """Facade: приховує репозиторії, політики й шину подій від клієнтського коду.

    Усі операції запису виконуються під одним блокуванням ``_write_lock``,
    тому складні дії (перевірка доступності + позначення книги як виданої)
    є атомарними з погляду інших потоків. Читання блокує лише репозиторій.
    """

    def __init__(
        self,
        policy: LoanPolicy | None = None,
        events: EventBus | None = None,
        latency: float = 0.0,
    ) -> None:
        self.authors: Repository[Author] = Repository("Автора", latency)
        self.books: Repository[Book] = Repository("Книгу", latency)
        self.readers: Repository[Reader] = Repository("Читача", latency)
        self.policy = policy or StandardPolicy()
        self.events = events or EventBus()
        self._write_lock = threading.RLock()

    # ----- Автори та книги -------------------------------------------------

    @log_call
    def add_author(self, name: str, birth_year: int | None = None) -> Author:
        with self._write_lock:
            return self.authors.add(Author(name, birth_year))

    @log_call
    def add_book(self, title: str, isbn: str, year: int, author: Author) -> Book:
        return self._insert_book(Book(title, isbn, year, author))

    @log_call
    def import_book(self, record: Mapping[str, Any]) -> Book:
        """Імпорт книги із зовнішнього запису (рядок CSV, JSON-об'єкт тощо).

        Якщо запис некоректний, автор, створений саме для цього запису,
        видаляється, щоб не лишилось «осиротілих» авторів.
        """
        author_name = record.get("author") if isinstance(record, Mapping) else None
        non_empty_str("author", author_name)
        with self._write_lock:
            existing = self._find_author(author_name)
            author = existing or self.authors.add(Author(author_name))
            try:
                book = BookFactory.from_record(record, author)
            except ValidationError:
                if existing is None:
                    self.authors.remove(author.id)
                raise
            return self._insert_book(book)

    def _find_author(self, name: str) -> Author | None:
        key = name.strip().casefold()
        matches = self.authors.find(lambda a: a.name.casefold() == key)
        return matches[0] if matches else None

    def _insert_book(self, book: Book) -> Book:
        with self._write_lock:
            if self.books.find(lambda b: b.isbn == book.isbn):
                raise DuplicateError(f"Книга з ISBN {book.isbn} вже є у каталозі")
            return self.books.add(book)

    # ----- Читачі ----------------------------------------------------------

    @log_call
    def register_reader(self, name: str, email: str) -> Reader:
        valid_email("email", email)
        key = email.strip().lower()
        with self._write_lock:
            if self.readers.find(lambda r: r.email == key):
                raise DuplicateError(f"Читач з e-mail {key} вже зареєстрований")
            return self.readers.add(Reader(name, email))

    # ----- Позички ---------------------------------------------------------

    @log_call
    def borrow_book(self, reader_id: int, book_id: int) -> Book:
        with self._write_lock:
            reader = self.readers.get(reader_id)
            book = self.books.get(book_id)
            if not book.is_available:
                raise BookUnavailableError(f"Книга '{book.title}' уже видана")
            if not self.policy.allows(reader):
                limit = self.policy.max_loans(reader)
                raise LoanLimitError(f"Читач '{reader.name}' досяг ліміту {limit} позичок")
            book.borrowed_by = reader.id
            reader.borrowed_ids.add(book.id)
            payload = {
                "reader_id": reader.id,
                "reader_email": reader.email,
                "book_id": book.id,
                "title": book.title,
            }
        # Події публікуються поза блокуванням, щоб не утримувати його довше потрібного
        self.events.publish("book_borrowed", payload)
        return book

    @log_call
    def return_book(self, reader_id: int, book_id: int) -> Book:
        with self._write_lock:
            reader = self.readers.get(reader_id)
            book = self.books.get(book_id)
            if book.borrowed_by != reader.id:
                raise NotBorrowedError(f"Книга '{book.title}' не видана читачеві '{reader.name}'")
            book.borrowed_by = None
            reader.borrowed_ids.discard(book.id)
            payload = {
                "reader_id": reader.id,
                "reader_email": reader.email,
                "book_id": book.id,
                "title": book.title,
            }
        self.events.publish("book_returned", payload)
        return book

    # ----- Пошук -----------------------------------------------------------

    def search_books(self, query: str) -> list[Book]:
        """Пошук книг за підрядком у назві (без урахування регістру)."""
        non_empty_str("query", query)
        needle = query.strip().casefold()
        found = self.books.find(lambda b: needle in b.title.casefold())
        return sorted(found, key=lambda b: b.title)

    def available_books(self) -> list[Book]:
        return self.books.find(lambda b: b.is_available)
