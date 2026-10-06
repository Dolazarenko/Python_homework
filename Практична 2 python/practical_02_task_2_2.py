"""Конвеєр генераторів для обробки даних про оцінки студентів."""

from collections import defaultdict

SAMPLE_DATA = [
    "Олена,Математика,95",
    "Іван,Математика,78",
    "",
    "Марія,Фізика,92",
    "Петро,Математика,INVALID",
    "Анна,Фізика,88",
    "Олена,Фізика,90",
    "Іван,Програмування,85",
    "Марія,Програмування,91",
    "Петро,Фізика,76",
    "Анна,Математика,93",
    "Олена,Програмування,97",
    "",
    "Марія,Математика,89",
    "Іван,Фізика,72",
    "Петро,Програмування,80",
    "Анна,Програмування,86",
]


def data_source(records: list[str]):
    """Етап 1: видає записи по одному."""
    for record in records:
        yield record


def filter_empty(records):
    """Етап 2: пропускає порожні рядки."""
    for record in records:
        if record.strip():
            yield record


def parse_records(records):
    """Етап 3: парсинг рядків у словники; некоректні записи пропускаються."""
    for record in records:
        parts = record.split(",")
        if len(parts) != 3:
            continue
        student, subject, grade_str = (p.strip() for p in parts)
        try:
            grade = int(grade_str)
        except ValueError:
            continue
        yield {"student": student, "subject": subject, "grade": grade}


def filter_passed(records, min_grade: int = 60):
    """Етап 4: залишає записи з оцінкою >= min_grade."""
    for rec in records:
        if rec["grade"] >= min_grade:
            yield rec


def format_output(records):
    """Етап 5: форматування для виведення."""
    for rec in records:
        yield f"[{rec['subject']}] {rec['student']}: {rec['grade']} балів"


def average_by_subject(records):
    """Другий конвеєр, кінцевий етап: середній бал по предметах."""
    subject_grades = defaultdict(list)
    for rec in records:
        subject_grades[rec["subject"]].append(rec["grade"])
    for subject, grades in sorted(subject_grades.items()):
        yield subject, sum(grades) / len(grades), len(grades)


def main():
    pipeline = format_output(
        filter_passed(
            parse_records(
                filter_empty(
                    data_source(SAMPLE_DATA)
                )
            ),
            min_grade=75,
        )
    )

    print("=== Результати (>= 75 балів) ===")
    for line in pipeline:
        print(line)

    print("\n=== Середній бал по предметах ===")
    pipeline2 = average_by_subject(
        parse_records(filter_empty(data_source(SAMPLE_DATA)))
    )
    for subject, avg, count in pipeline2:
        print(f"  {subject}: {avg:.1f} (з {count} оцінок)")


if __name__ == "__main__":
    main()
