"""Тести фасаду LibraryService, політики позичання та шини подій."""
import unittest

from library import (
    BookUnavailableError,
    DuplicateError,
    LibraryService,
    LoanLimitError,
    NotBorrowedError,
    NotFoundError,
    ValidationError,
)
from library.patterns import StandardPolicy
from library.validators import make_isbn13


def make_library(policy=None, books=2):
    lib = LibraryService(policy=policy)
    author = lib.add_author("Автор")
    book_list = [
        lib.add_book(f"Книга {i}", make_isbn13(f"{i:09d}"), 2000, author)
        for i in range(1, books + 1)
    ]
    reader = lib.register_reader("Читач", "reader@example.com")
    return lib, reader, book_list


class BorrowingTests(unittest.TestCase):
    def test_borrow_and_return(self):
        lib, reader, (book, _) = make_library()
        lib.borrow_book(reader.id, book.id)
        self.assertFalse(book.is_available)
        self.assertIn(book.id, reader.borrowed_ids)
        lib.return_book(reader.id, book.id)
        self.assertTrue(book.is_available)
        self.assertEqual(reader.borrowed_ids, set())

    def test_book_already_borrowed(self):
        lib, reader, (book, _) = make_library()
        other = lib.register_reader("Інший", "other@example.com")
        lib.borrow_book(reader.id, book.id)
        with self.assertRaises(BookUnavailableError):
            lib.borrow_book(other.id, book.id)

    def test_return_by_wrong_reader(self):
        lib, reader, (book, _) = make_library()
        other = lib.register_reader("Інший", "other@example.com")
        lib.borrow_book(reader.id, book.id)
        with self.assertRaises(NotBorrowedError):
            lib.return_book(other.id, book.id)

    def test_loan_limit_default_policy(self):
        lib, reader, _ = make_library(books=4)
        books = lib.books.all()
        for book in books[:3]:
            lib.borrow_book(reader.id, book.id)
        with self.assertRaises(LoanLimitError):
            lib.borrow_book(reader.id, books[3].id)

    def test_unknown_reader_is_not_found(self):
        lib, _, (book, _) = make_library()
        with self.assertRaises(NotFoundError):
            lib.borrow_book(9999, book.id)


class CatalogTests(unittest.TestCase):
    def test_duplicate_isbn_rejected(self):
        lib, _, (book, _) = make_library()
        with self.assertRaises(DuplicateError):
            lib.add_book("Копія", book.isbn, 2001, book.author)

    def test_duplicate_email_rejected(self):
        lib, _, _ = make_library()
        with self.assertRaises(DuplicateError):
            lib.register_reader("Двійник", "reader@example.com")

    def test_invalid_email_rejected_before_lookup(self):
        lib = LibraryService()
        with self.assertRaises(ValidationError):
            lib.register_reader("Іван", None)

    def test_invalid_import_leaves_no_orphan_author(self):
        lib = LibraryService()
        with self.assertRaises(ValidationError):
            lib.import_book({
                "title": "",
                "isbn": make_isbn13("000000030"),
                "year": 2000,
                "author": "Новий автор",
            })
        self.assertEqual(len(lib.authors), 0)

    def test_import_reuses_author_case_insensitively(self):
        lib = LibraryService()
        lib.import_book({"title": "Перша", "isbn": make_isbn13("000000031"),
                         "year": "1900", "author": "Іван Франко"})
        lib.import_book({"title": "Друга", "isbn": make_isbn13("000000032"),
                         "year": 1901, "author": "  іван франко  "})
        self.assertEqual(len(lib.authors), 1)
        self.assertEqual(len(lib.books), 2)

    def test_import_missing_author(self):
        lib = LibraryService()
        with self.assertRaises(ValidationError):
            lib.import_book({"title": "Без автора", "isbn": make_isbn13("000000033"), "year": 2000})

    def test_search_is_case_insensitive(self):
        lib = LibraryService()
        lib.import_book({"title": "Захар Беркут", "isbn": make_isbn13("000000034"),
                         "year": 1883, "author": "Франко"})
        found = lib.search_books("захар")
        self.assertEqual([b.title for b in found], ["Захар Беркут"])


class EventAndPolicyTests(unittest.TestCase):
    def test_subscriber_receives_borrow_event(self):
        lib, reader, (book, _) = make_library()
        received = []
        lib.events.subscribe("book_borrowed", received.append)
        lib.borrow_book(reader.id, book.id)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["title"], book.title)
        self.assertEqual(received[0]["reader_email"], reader.email)

    def test_failing_subscriber_is_isolated(self):
        lib, reader, (book, _) = make_library()

        def broken(_payload):
            raise RuntimeError("збій обробника")

        received = []
        lib.events.subscribe("book_borrowed", broken)
        lib.events.subscribe("book_borrowed", received.append)
        with self.assertLogs("library.events", level="ERROR"):
            lib.borrow_book(reader.id, book.id)
        self.assertEqual(len(received), 1)
        self.assertFalse(book.is_available)

    def test_custom_strategy_is_applied(self):
        lib, reader, (first, second) = make_library(policy=StandardPolicy(limit=1))
        lib.borrow_book(reader.id, first.id)
        with self.assertRaises(LoanLimitError):
            lib.borrow_book(reader.id, second.id)


if __name__ == "__main__":
    unittest.main()
