"""Ітерабельний контейнер StudentGroup з окремим ітератором."""

from collections import namedtuple

Student = namedtuple("Student", ["name", "grade"])


class StudentGroupIterator:
    """Ітератор для обходу StudentGroup."""

    def __init__(self, students: list[Student]):
        self._students = students
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Student:
        if self._index >= len(self._students):
            raise StopIteration
        student = self._students[self._index]
        self._index += 1
        return student


class StudentGroup:
    """Ітерабельний контейнер студентів з підтримкою багаторазового обходу."""

    def __init__(self, group_name: str):
        self._group_name = group_name
        self._students: list[Student] = []

    def add_student(self, name: str, grade: int) -> None:
        """Додає студента до групи."""
        self._students.append(Student(name, grade))

    def __iter__(self):
        # Новий ітератор при кожному виклику -> багаторазовий обхід
        return StudentGroupIterator(self._students)

    def __len__(self) -> int:
        return len(self._students)

    def top_students(self, n: int = 3):
        """Повертає ітератор по n найкращих студентах."""
        ordered = sorted(self._students, key=lambda s: s.grade, reverse=True)
        return iter(ordered[:n])


def main():
    group = StudentGroup("КІ-21")
    group.add_student("Олена", 95)
    group.add_student("Іван", 78)
    group.add_student("Марія", 92)
    group.add_student("Петро", 85)
    group.add_student("Анна", 88)

    print("Перший обхід:")
    for student in group:
        print(f"  {student.name}: {student.grade}")

    print("\nДругий обхід:")
    for student in group:
        print(f"  {student.name}: {student.grade}")

    # Два незалежні ітератори одночасно (вкладений цикл)
    print("\nВсі пари студентів:")
    for s1 in group:
        for s2 in group:
            if s1.name < s2.name:
                print(f"  {s1.name} та {s2.name}")

    print("\nТоп-3 студенти:")
    for student in group.top_students(3):
        print(f"  {student.name}: {student.grade}")


if __name__ == "__main__":
    main()
