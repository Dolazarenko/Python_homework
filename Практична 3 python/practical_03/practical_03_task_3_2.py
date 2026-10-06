# practical_03_task_3_2.py

"""Паттерни Observer, Strategy та архітектурний шаблон MVC."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable


# --- Observer ---

class EventEmitter:
    """Базовий клас для підтримки системи подій (Observer)."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """Підписатися на подію."""
        self._listeners.setdefault(event, []).append(callback)

    def off(self, event: str, callback: Callable):
        """Відписатися від події."""
        listeners = self._listeners.get(event, [])
        if callback in listeners:
            listeners.remove(callback)

    def emit(self, event: str, *args, **kwargs):
        """Сповістити всіх слухачів про подію."""
        # Копія списку — слухач може відписатися під час виклику
        for callback in list(self._listeners.get(event, [])):
            callback(*args, **kwargs)


# --- Strategy ---

class SortStrategy(ABC):
    """Абстрактна стратегія сортування завдань."""

    @abstractmethod
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        ...


class SortByPriority(SortStrategy):
    """Сортування за пріоритетом (високий → низький)."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        # 1 — найвищий пріоритет, тому за зростанням числа
        return sorted(tasks, key=lambda t: t.priority)


class SortByDeadline(SortStrategy):
    """Сортування за терміном виконання (найближчий першим)."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda t: t.deadline)


class SortByCreationDate(SortStrategy):
    """Сортування за датою створення (найновіші першими)."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)


# --- Model ---

@dataclass
class Task:
    title: str
    priority: int  # 1 (найвищий) – 5 (найнижчий)
    deadline: datetime
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class TaskModel(EventEmitter):
    """Model: дані та бізнес-логіка завдань."""

    def __init__(self):
        super().__init__()
        self._tasks: list[Task] = []

    def add_task(self, title: str, priority: int, deadline: datetime):
        if not 1 <= priority <= 5:
            raise ValueError("Пріоритет має бути від 1 до 5")
        task = Task(title, priority, deadline)
        self._tasks.append(task)
        self.emit("task_added", task)

    def complete_task(self, index: int):
        task = self._tasks[index]
        task.completed = True
        self.emit("task_completed", task)

    def remove_task(self, index: int):
        task = self._tasks.pop(index)
        self.emit("task_removed", task)

    def get_tasks(self, include_completed: bool = True) -> list[Task]:
        if include_completed:
            return list(self._tasks)
        return [t for t in self._tasks if not t.completed]

    def get_statistics(self) -> dict:
        total = len(self._tasks)
        done = sum(t.completed for t in self._tasks)
        return {"всього": total, "виконано": done, "активних": total - done}


# --- View ---

class TaskView:
    """View: відображення даних у консолі."""

    def show_tasks(self, tasks: list[Task], title: str = "Завдання"):
        print(f"\n=== {title} ===")
        if not tasks:
            print("  (порожньо)")
            return
        header = f"{'№':<3} {'Назва':<28} {'Пріор.':<7} {'Дедлайн':<17} Статус"
        print(header)
        print("-" * len(header))
        for i, t in enumerate(tasks, 1):
            status = "виконано" if t.completed else "активне"
            deadline = f"{t.deadline:%Y-%m-%d %H:%M}"
            print(f"{i:<3} {t.title:<28} {t.priority:<7} {deadline:<17} {status}")

    def show_message(self, message: str):
        print(f"[INFO] {message}")

    def show_statistics(self, stats: dict):
        print("\n=== Статистика ===")
        for key, value in stats.items():
            print(f"  {key.capitalize()}: {value}")


# --- Controller ---

class TaskController:
    """Controller: координація Model та View з підтримкою Strategy."""

    def __init__(self, model: TaskModel, view: TaskView):
        self._model = model
        self._view = view
        self._sort_strategy: SortStrategy = SortByPriority()

        # Observer: підписка на події моделі
        model.on("task_added", lambda t: view.show_message(
            f"Додано завдання: «{t.title}» (пріоритет {t.priority})"))
        model.on("task_completed", lambda t: view.show_message(
            f"Завдання виконано: «{t.title}»"))
        model.on("task_removed", lambda t: view.show_message(
            f"Завдання видалено: «{t.title}»"))

    def set_sort_strategy(self, strategy: SortStrategy):
        """Змінити стратегію сортування (Strategy)."""
        self._sort_strategy = strategy

    def add_task(self, title: str, priority: int, deadline: datetime):
        self._model.add_task(title, priority, deadline)

    def complete_task(self, index: int):
        # index — позиція завдання в порядку додавання (0-based)
        self._model.complete_task(index)

    def remove_task(self, index: int):
        self._model.remove_task(index)

    def show_all(self):
        tasks = self._model.get_tasks()
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(sorted_tasks)

    def show_active(self):
        tasks = self._model.get_tasks(include_completed=False)
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(sorted_tasks, title="Активні завдання")

    def show_stats(self):
        self._view.show_statistics(self._model.get_statistics())


def main():
    model = TaskModel()
    view = TaskView()
    ctrl = TaskController(model, view)

    now = datetime.now()
    ctrl.add_task("Здати практичну роботу", 1, now + timedelta(days=2))
    ctrl.add_task("Купити продукти", 4, now + timedelta(days=1))
    ctrl.add_task("Підготуватися до іспиту", 2, now + timedelta(days=7))
    ctrl.add_task("Записатися до лікаря", 3, now + timedelta(days=5))
    ctrl.add_task("Прочитати книгу", 5, now + timedelta(days=30))

    ctrl.set_sort_strategy(SortByPriority())
    view.show_message("Сортування за пріоритетом")
    ctrl.show_all()

    ctrl.set_sort_strategy(SortByDeadline())
    view.show_message("Сортування за дедлайном")
    ctrl.show_all()

    ctrl.set_sort_strategy(SortByCreationDate())
    view.show_message("Сортування за датою створення")
    ctrl.show_all()

    print()
    ctrl.complete_task(0)  # «Здати практичну роботу»

    ctrl.set_sort_strategy(SortByPriority())
    ctrl.show_active()
    ctrl.show_stats()


if __name__ == "__main__":
    main()
