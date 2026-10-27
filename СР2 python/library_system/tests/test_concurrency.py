"""Тести потокобезпечності: конкуренція за книги, ліміти, унікальність даних."""
import unittest

from library import BookUnavailableError, DuplicateError, LibraryService, LoanLimitError
from library.concurrency import run_requests
from library.validators import make_isbn13


class ConcurrencyTests(unittest.TestCase):
    def test_single_book_is_borrowed_exactly_once(self):
        lib = LibraryService()
        author = lib.add_author("Автор")
        book = lib.add_book("Єдина книга", make_isbn13("000000001"), 2000, author)
        readers = [lib.register_reader(f"Читач {i}", f"r{i}@lib.ua") for i in range(50)]
        events = []
        lib.events.subscribe("book_borrowed", events.append)

        results = run_requests(
            [lambda r=r: lib.borrow_book(r.id, book.id) for r in readers],
            max_workers=16,
        )

        successes = [r for r in results if r.ok]
        failures = [r for r in results if not r.ok]
        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 49)
        self.assertTrue(all(isinstance(r.error, BookUnavailableError) for r in failures))
        self.assertEqual(len(events), 1)
        self.assertIn(book.borrowed_by, {r.id for r in readers})

    def test_reader_limit_holds_under_concurrency(self):
        lib = LibraryService()
        author = lib.add_author("Автор")
        books = [
            lib.add_book(f"Книга {i}", make_isbn13(f"{i:09d}"), 2000, author)
            for i in range(1, 11)
        ]
        reader = lib.register_reader("Жадібний", "greedy@lib.ua")

        results = run_requests(
            [lambda b=b: lib.borrow_book(reader.id, b.id) for b in books],
            max_workers=10,
        )

        self.assertEqual(sum(r.ok for r in results), 3)
        self.assertEqual(sum(isinstance(r.error, LoanLimitError) for r in results), 7)
        self.assertEqual(len(reader.borrowed_ids), 3)

    def test_concurrent_imports_keep_data_consistent(self):
        lib = LibraryService()
        records = [
            {"title": f"Книга {i}", "isbn": make_isbn13(f"{i:09d}"),
             "year": 2000, "author": f"Автор {i % 7}"}
            for i in range(1, 201)
        ]

        results = run_requests(
            [lambda rec=rec: lib.import_book(rec) for rec in records],
            max_workers=16,
        )

        self.assertTrue(all(r.ok for r in results), [str(r.error) for r in results if not r.ok][:3])
        ids = [b.id for b in lib.books.all()]
        self.assertEqual(len(ids), 200)
        self.assertEqual(len(set(ids)), 200)
        self.assertEqual(len(lib.authors), 7)  # без дублікатів авторів

    def test_duplicate_isbn_race(self):
        lib = LibraryService()
        author = lib.add_author("Автор")
        isbn = make_isbn13("000000777")

        results = run_requests(
            [lambda: lib.add_book("Дубль", isbn, 2000, author) for _ in range(30)],
            max_workers=10,
        )

        self.assertEqual(sum(r.ok for r in results), 1)
        self.assertEqual(sum(isinstance(r.error, DuplicateError) for r in results), 29)
        self.assertEqual(len(lib.books), 1)

    def test_results_keep_submission_order(self):
        results = run_requests([lambda i=i: i * i for i in range(20)], max_workers=6)
        self.assertEqual([r.index for r in results], list(range(20)))
        self.assertEqual([r.value for r in results], [i * i for i in range(20)])


if __name__ == "__main__":
    unittest.main()
