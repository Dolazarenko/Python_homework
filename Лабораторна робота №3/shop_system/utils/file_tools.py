"""Утиліти для роботи з файлами, зокрема власний контекстний менеджер.

Docstring рівня модуля (Завдання 4). Контекстний менеджер тут
використовується для демонстрації Завдання 1.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import TracebackType
from typing import Any, Optional


class JsonCatalogReader:
    """Власний контекстний менеджер для читання JSON-каталогу товарів.

    Гарантує коректне закриття файлового дескриптора навіть у разі
    виключення всередині блоку ``with`` — це замінює ручну конструкцію
    ``try/finally``, оскільки метод ``__exit__`` викликається автоматично
    незалежно від того, чи сталася помилка в тілі блоку ``with``.

    Args:
        path: Шлях до JSON-файлу каталогу.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._file = None

    def __enter__(self) -> "JsonCatalogReader":
        self._file = open(self.path, "r", encoding="utf-8")
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        if self._file is not None:
            self._file.close()
        # False -> не пригнічуємо виключення, лише гарантовано звільняємо ресурс.
        return False

    def read(self) -> list[dict[str, Any]]:
        """Зчитує та парсить JSON-вміст файлу.

        Returns:
            Список словників із даними товарів.

        Raises:
            json.JSONDecodeError: якщо вміст файлу не є коректним JSON.
        """
        assert self._file is not None
        return json.load(self._file)


def read_text_file_with_context_manager(path: str) -> str:
    """Демонструє стандартний вбудований контекстний менеджер ``with open(...)``.

    Args:
        path: Шлях до текстового файлу.

    Returns:
        Вміст файлу як рядок.

    Raises:
        FileNotFoundError: якщо файл не існує.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def ensure_directory(path: str) -> Path:
    """Створює директорію, якщо вона ще не існує.

    Args:
        path: Шлях до директорії.

    Returns:
        Об'єкт ``Path`` створеної або наявної директорії.
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
