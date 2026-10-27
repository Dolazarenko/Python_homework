# practical_04_task_3_2.py

"""Producer-Consumer з queue.Queue та демонстрація дедлоку."""

import threading
import queue
import time
import random


class Task:
    """Завдання для обробки."""

    def __init__(self, task_id: int, data: str, priority: int = 0):
        self.task_id = task_id
        self.data = data
        self.priority = priority
        self.created_at = time.time()

    def __repr__(self):
        return f"Task(id={self.task_id}, data='{self.data}')"


def producer(task_queue: queue.Queue, num_tasks: int,
             producer_id: int) -> None:
    """Виробник: генерує завдання та поміщає їх у чергу.

    Сигнал завершення (None) надсилає головний потік після того, як усі
    виробники завершилися — інакше перший, що закінчив, зупинив би
    споживачів, поки інший ще виробляє.
    """
    for i in range(num_tasks):
        task = Task(
            task_id=producer_id * 100 + i,
            data=f"Дані від виробника {producer_id}, пакет {i}",
            priority=random.randint(1, 5),
        )
        task_queue.put(task)  # блокується, якщо черга повна (зворотний тиск)
        print(f"[Виробник-{producer_id}] Створено {task} (розмір черги ≈ {task_queue.qsize()})")
        time.sleep(random.uniform(0.1, 0.3))
    print(f"[Виробник-{producer_id}] Завершив")


def consumer(task_queue: queue.Queue, consumer_id: int,
             results: list, results_lock: threading.Lock) -> None:
    """Споживач: обробляє завдання з черги."""
    while True:
        try:
            task = task_queue.get(timeout=2)
        except queue.Empty:
            print(f"  [Споживач-{consumer_id}] Черга порожня, завершення")
            break

        if task is None:
            # Передати сигнал завершення наступному споживачу
            task_queue.task_done()
            task_queue.put(None)
            break

        try:
            started = time.time()
            time.sleep(random.uniform(0.1, 0.4))  # імітація роботи
            processing_time = time.time() - started
            with results_lock:
                results.append({
                    "task_id": task.task_id,
                    "consumer": consumer_id,
                    "processing_time": processing_time,
                    "latency": time.time() - task.created_at,
                })
            print(f"  [Споживач-{consumer_id}] Оброблено {task} за {processing_time:.2f} сек")
        finally:
            task_queue.task_done()


def producer_consumer_demo():
    """Демонстрація паттерну Producer-Consumer."""
    task_queue = queue.Queue(maxsize=5)
    results: list = []
    results_lock = threading.Lock()
    num_producers = 2
    num_consumers = 3
    tasks_per_producer = 5

    producers = [
        threading.Thread(target=producer, args=(task_queue, tasks_per_producer, pid),
                         name=f"Producer-{pid}")
        for pid in range(1, num_producers + 1)
    ]
    consumers = [
        threading.Thread(target=consumer, args=(task_queue, cid, results, results_lock),
                         name=f"Consumer-{cid}")
        for cid in range(1, num_consumers + 1)
    ]

    for t in consumers + producers:
        t.start()

    for t in producers:
        t.join()
    task_queue.put(None)  # sentinel: споживачі передають його далі один одному
    for t in consumers:
        t.join()

    expected = num_producers * tasks_per_producer
    avg = sum(r["processing_time"] for r in results) / len(results) if results else 0.0
    print(f"\nОброблено задач: {len(results)} з {expected}")
    print(f"Середній час обробки: {avg:.3f} сек")
    per_consumer = {}
    for r in results:
        per_consumer[r["consumer"]] = per_consumer.get(r["consumer"], 0) + 1
    for cid in sorted(per_consumer):
        print(f"  Споживач-{cid}: {per_consumer[cid]} задач")


def deadlock_demo():
    """Демонстрація та виявлення потенційного дедлоку."""
    lock_a = threading.Lock()
    lock_b = threading.Lock()
    deadlock_detected = threading.Event()

    def worker_1():
        """Захоплює lock_a, потім lock_b."""
        lock_a.acquire()
        print("[Worker-1] Захопив Lock A")
        time.sleep(0.1)
        acquired = lock_b.acquire(timeout=2)
        if not acquired:
            print("[Worker-1] ДЕДЛОК: не вдалося захопити Lock B!")
            deadlock_detected.set()
            lock_a.release()
            return
        print("[Worker-1] Захопив Lock B")
        lock_b.release()
        lock_a.release()

    def worker_2():
        """Захоплює lock_b, потім lock_a — зворотний порядок!"""
        lock_b.acquire()
        print("[Worker-2] Захопив Lock B")
        time.sleep(0.1)
        acquired = lock_a.acquire(timeout=2)
        if not acquired:
            print("[Worker-2] ДЕДЛОК: не вдалося захопити Lock A!")
            deadlock_detected.set()
            lock_b.release()
            return
        print("[Worker-2] Захопив Lock A")
        lock_a.release()
        lock_b.release()

    safe_done = []

    def safe_worker_1():
        """Безпечна версія: завжди захоплює A → B."""
        with lock_a:
            print("[Safe-1] Захопив Lock A")
            time.sleep(0.1)
            with lock_b:
                print("[Safe-1] Захопив Lock B")
        safe_done.append(1)

    def safe_worker_2():
        """Безпечна версія: той самий порядок A → B."""
        with lock_a:
            print("[Safe-2] Захопив Lock A")
            time.sleep(0.1)
            with lock_b:
                print("[Safe-2] Захопив Lock B")
        safe_done.append(2)

    # === Демонстрація дедлоку ===
    print("=== Спроба з потенційним дедлоком ===")
    t1 = threading.Thread(target=worker_1)
    t2 = threading.Thread(target=worker_2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    if deadlock_detected.is_set():
        print(">>> Дедлок виявлено! Використовуємо timeout для запобігання зависанню.\n")
    else:
        print(">>> Дедлок не виник цього разу (залежить від планувальника).\n")

    # === Безпечна версія ===
    print("=== Безпечна версія (однаковий порядок замків) ===")
    s1 = threading.Thread(target=safe_worker_1)
    s2 = threading.Thread(target=safe_worker_2)
    s1.start()
    s2.start()
    s1.join()
    s2.join()
    print(f">>> Обидва потоки завершилися ({len(safe_done)}/2), дедлоку немає.")


def main():
    print("=" * 60)
    print("=== Паттерн Producer-Consumer ===")
    print("=" * 60)
    producer_consumer_demo()

    print(f"\n{'=' * 60}")
    print("=== Демонстрація дедлоку ===")
    print("=" * 60)
    deadlock_demo()


if __name__ == "__main__":
    main()
