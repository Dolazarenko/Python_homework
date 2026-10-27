"""Ієрархія власних винятків бібліотечної системи."""


class LibraryError(Exception):
    """Базовий виняток для всіх помилок бібліотечної системи."""


class ValidationError(LibraryError, ValueError):
    """Некоректні вхідні дані."""


class NotFoundError(LibraryError):
    """Сутність із заданим ідентифікатором не знайдено."""


class DuplicateError(LibraryError):
    """Спроба додати сутність, яка вже існує (наприклад, та сама адреса e-mail)."""


class BookUnavailableError(LibraryError):
    """Книга вже видана іншому читачеві."""


class LoanLimitError(LibraryError):
    """Перевищено ліміт одночасних позичок."""


class NotBorrowedError(LibraryError):
    """Спроба повернути книгу, яку читач не брав."""
