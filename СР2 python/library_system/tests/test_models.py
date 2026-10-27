"""Тести метакласу, моделей, валідації та фабрики."""
import unittest

from library import Author, Book, Reader, ValidationError
from library.factories import BookFactory
from library.logging_meta import TrackedMeta
from library.validators import make_isbn13


class MetaclassTests(unittest.TestCase):
    def test_creation_is_logged(self):
        with self.assertLogs("library.objects", level="INFO") as logs:
            Author("Леся Українка", 1871)
        self.assertTrue(any("Створено Author" in msg for msg in logs.output))

    def test_instance_counter(self):
        before = TrackedMeta.instances_created(Reader)
        Reader("Іван", "ivan@example.com")
        Reader("Олена", "olena@example.com")
        self.assertEqual(TrackedMeta.instances_created(Reader), before + 2)

    def test_failed_creation_is_not_counted(self):
        before = TrackedMeta.instances_created(Author)
        with self.assertRaises(ValidationError):
            Author("")
        self.assertEqual(TrackedMeta.instances_created(Author), before)

    def test_models_are_registered(self):
        self.assertIs(TrackedMeta.registry["Book"], Book)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.author = Author("Тарас Шевченко")
        self.isbn = make_isbn13("000000001")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValidationError):
            Author("   ")

    def test_birth_year_out_of_range(self):
        with self.assertRaises(ValidationError):
            Author("Хтось", birth_year=3000)

    def test_invalid_isbn_format(self):
        with self.assertRaises(ValidationError):
            Book("Назва", "123", 2000, self.author)

    def test_isbn13_bad_checksum(self):
        broken = self.isbn[:-1] + str((int(self.isbn[-1]) + 1) % 10)
        with self.assertRaises(ValidationError):
            Book("Назва", broken, 2000, self.author)

    def test_isbn10_accepted_and_normalized(self):
        book = Book("Назва", "0-306-40615-2", 2000, self.author)
        self.assertEqual(book.isbn, "0306406152")

    def test_isbn13_normalized(self):
        book = Book("Назва", "978-0-306-40615-7", 2000, self.author)
        self.assertEqual(book.isbn, "9780306406157")

    def test_future_year_rejected(self):
        with self.assertRaises(ValidationError):
            Book("Назва", self.isbn, 3000, self.author)

    def test_boolean_year_rejected(self):
        with self.assertRaises(ValidationError):
            Book("Назва", self.isbn, True, self.author)

    def test_author_must_be_author_instance(self):
        with self.assertRaises(ValidationError):
            Book("Назва", self.isbn, 2000, "Шевченко")

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            Reader("Іван", "ivan-at-mail")


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.author = Author("Леся Українка")
        self.isbn = make_isbn13("000000002")

    def test_year_converted_from_string(self):
        book = BookFactory.from_record(
            {"title": "Лісова пісня", "isbn": self.isbn, "year": "1911"}, self.author
        )
        self.assertEqual(book.year, 1911)

    def test_missing_field_reported(self):
        with self.assertRaisesRegex(ValidationError, "isbn"):
            BookFactory.from_record({"title": "X", "year": 1900}, self.author)

    def test_non_numeric_year(self):
        with self.assertRaises(ValidationError):
            BookFactory.from_record(
                {"title": "X", "isbn": self.isbn, "year": "двадцять"}, self.author
            )

    def test_non_mapping_record(self):
        with self.assertRaises(ValidationError):
            BookFactory.from_record(["X"], self.author)


if __name__ == "__main__":
    unittest.main()
