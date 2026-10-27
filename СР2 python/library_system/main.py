"""Демонстраційний сценарій: імпорт з помилками, реєстрація, паралельні позички."""
import logging

from library import LibraryError, LibraryService
from library.concurrency import run_requests
from library.validators import make_isbn13


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    lib = LibraryService()

    # Observer: підписники на події позичання та повернення
    lib.events.subscribe(
        "book_borrowed",
        lambda p: print(f"  → Сповіщення: '{p['title']}' видано ({p['reader_email']})"),
    )
    lib.events.subscribe("book_returned", lambda p: print(f"  ← Повернено: '{p['title']}'"))

    print("=== 1. Імпорт книг (частина записів містить помилки) ===")
    records = [
        {"title": "Кобзар", "isbn": make_isbn13("000000001"), "year": "1840", "author": "Тарас Шевченко"},
        {"title": "Лісова пісня", "isbn": "0-306-40615-2", "year": 1911, "author": "Леся Українка"},
        {"title": "Тіні забутих предків", "isbn": make_isbn13("000000002"), "year": 1911, "author": "Михайло Коцюбинський"},
        {"title": "Битий ISBN", "isbn": "123-456", "year": 2000, "author": "Невідомий"},
        {"title": "", "isbn": make_isbn13("000000003"), "year": 2000, "author": "Хтось"},
        {"title": "Без року", "isbn": make_isbn13("000000004"), "year": "двадцять", "author": "Хтось"},
        {"title": "Дубль", "isbn": make_isbn13("000000001"), "year": 1840, "author": "Тарас Шевченко"},
        {"title": "Без автора", "isbn": make_isbn13("000000005"), "year": 2000},
    ]
    for record in records:
        try:
            book = lib.import_book(record)
            print(f"  OK     {book.title!r} (ISBN {book.isbn})")
        except LibraryError as exc:
            print(f"  ПОМИЛКА: {exc}")
    print(f"  Авторів у системі: {len(lib.authors)} (без «осиротілих» після помилок)")

    print("\n=== 2. Додаткові книги та читачі ===")
    author = lib.add_author("Анонімний збірник", birth_year=None)
    for i in range(1, 6):
        lib.add_book(f"Збірка №{i}", make_isbn13(f"{100 + i:09d}"), 2000, author)
    readers = [lib.register_reader(f"Читач {i}", f"reader{i}@lib.ua") for i in range(1, 11)]
    try:
        lib.register_reader("Двійник", "reader1@lib.ua")
    except LibraryError as exc:
        print(f"  ПОМИЛКА: {exc}")

    print("\n=== 3. Десять читачів одночасно беруть одну книгу ===")
    kobzar = lib.search_books("Кобзар")[0]
    results = run_requests(
        [lambda r=r: lib.borrow_book(r.id, kobzar.id) for r in readers],
        max_workers=5,
    )
    winners = [r for r in results if r.ok]
    print(f"  Успішних позичок: {len(winners)}, відмов: {len(results) - len(winners)}")
    for r in results:
        status = "OK" if r.ok else type(r.error).__name__
        print(f"  запит #{r.index:02d} [{r.thread}] → {status}")

    print("\n=== 4. Ліміт позичок: один читач, шість паралельних запитів ===")
    limited = lib.register_reader("Ліміт", "limit@lib.ua")
    free = lib.available_books()[:6]
    results = run_requests(
        [lambda b=b: lib.borrow_book(limited.id, b.id) for b in free],
        max_workers=6,
    )
    print(f"  Успішних: {sum(r.ok for r in results)}, "
          f"відхилено через ліміт: {sum(not r.ok for r in results)}")

    print("\n=== 5. Повернення книги та пошук ===")
    holder = readers[winners[0].index]
    lib.return_book(holder.id, kobzar.id)
    print(f"  Вільні книги: {len(lib.available_books())} із {len(lib.books)}")
    print(f"  Пошук 'збірка': {[b.title for b in lib.search_books('збірка')]}")


if __name__ == "__main__":
    main()
