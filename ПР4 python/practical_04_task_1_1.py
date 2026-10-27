# practical_04_task_1_1.py

"""Створення та керування потоками в Python."""

import threading
import time


def download_simulation(file_name: str, size_mb: float) -> dict:
    """Імітація завантаження файлу (I/O-bound задача).

    Args:
        file_name: назва файлу.
        size_mb: розмір файлу в мегабайтах.

    Returns:
        Словник з інформацією про завантажений файл.
    """
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Початок завантаження '{file_name}' ({size_mb} MB)...")
    time.sleep(size_mb * 0.4)  # час пропорційний розміру
    print(f"[{thread_name}] Завершено '{file_name}'")
    return {"file": file_name, "size": size_mb, "thread": thread_name}


class MonitorThread(threading.Thread):
    """Потік-монітор, що періодично виводить стан системи."""

    def __init__(self, interval: float = 1.0):
        super().__init__(name="Monitor", daemon=True)
        self.interval = interval
        self.active_downloads = 0
        self._stop_event = threading.Event()

    def run(self):
        """Виводить кількість активних потоків кожні `interval` секунд."""
        # wait() повертає True, коли подія встановлена -> негайна зупинка
        while not self._stop_event.is_set():
            print(f"  [Monitor] Активних потоків: {threading.active_count()}")
            if self._stop_event.wait(self.interval):
                break

    def stop(self):
        self._stop_event.set()


def main():
    files = [
        ("data.csv", 2.5),
        ("report.pdf", 1.0),
        ("image.png", 0.5),
        ("archive.zip", 4.0),
        ("log.txt", 0.3),
    ]

    monitor = MonitorThread(interval=1.0)
    monitor.start()

    results: list = [None] * len(files)

    def worker(idx: int, name: str, size: float) -> None:
        results[idx] = download_simulation(name, size)

    threads = [
        threading.Thread(target=worker, args=(i, n, s), name=f"Downloader-{i + 1}")
        for i, (n, s) in enumerate(files)
    ]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start
    print(f"\nУсі файли завантажено за {elapsed:.2f} сек")

    monitor.stop()
    monitor.join()

    # Послідовне виконання для порівняння
    print("\n--- Послідовне виконання ---")
    start = time.perf_counter()
    for n, s in files:
        download_simulation(n, s)
    seq_elapsed = time.perf_counter() - start

    print(f"\nПаралельно:  {elapsed:.2f} сек")
    print(f"Послідовно:  {seq_elapsed:.2f} сек")
    print(f"Прискорення: {seq_elapsed / elapsed:.2f}x")


if __name__ == "__main__":
    main()
