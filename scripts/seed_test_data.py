import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

LECTURER_PASSWORD = "TestPass123!"
STUDENTS_PER_LECTURER = 24
ENROLLED_PER_COURSE = 10
RANDOM_SEED = 20261005

LECTURER_NAMES = [
    "Amina Bello", "Chinedu Okafor", "Fatima Ibrahim", "Emeka Nwosu",
    "Zainab Musa", "Tunde Adeyemi", "Ngozi Eze", "Bashir Abdullahi",
    "Kemi Adebayo", "Ibrahim Sani", "Adaobi Okeke", "Yusuf Lawal",
    "Bisi Ogunleye", "Obinna Uche", "Hauwa Umar", "Femi Bakare",
    "Chiamaka Obi", "Musa Danjuma", "Funke Salami", "Daniel Ekanem",
]

STUDENT_FIRST_NAMES = [
    "Adaeze", "Chinedu", "Fatima", "Ifeanyi", "Zainab", "Tunde",
    "Ngozi", "Bashir", "Kemi", "Emeka", "Aisha", "Obinna",
]

STUDENT_LAST_NAMES = [
    "Okafor", "Bello", "Eze", "Ibrahim", "Adeyemi", "Musa",
    "Nwosu", "Abdullahi", "Adebayo", "Uche", "Lawal", "Okeke",
]

DEPARTMENTS = [
    "Mechatronics Engineering",
    "Electrical/Electronic Engineering",
    "Mechanical Engineering",
]

LEVELS = ["200", "300", "400", "500"]

COURSES = [
    ("MCE 201", "Engineering Mathematics II", "200"),
    ("MCE 202", "Engineering Mechanics", "200"),
    ("MCE 203", "Circuit Theory", "200"),
    ("MCE 204", "Engineering Materials", "200"),
    ("MCE 205", "Computer Programming for Engineers", "200"),
    ("MCE 301", "Thermodynamics", "300"),
    ("MCE 302", "Fluid Mechanics", "300"),
    ("MCE 303", "Electrical Machines", "300"),
    ("MCE 304", "Manufacturing Technology", "300"),
    ("MCE 305", "Sensors and Instrumentation", "300"),
    ("MCE 401", "Control Systems Engineering", "400"),
    ("MCE 402", "Microprocessor Systems", "400"),
    ("MCE 403", "Robotics and Automation", "400"),
    ("MCE 404", "Machine Design", "400"),
    ("MCE 405", "Digital Signal Processing", "400"),
    ("MCE 501", "Industrial Automation", "500"),
    ("MCE 502", "Embedded Systems Design", "500"),
    ("MCE 503", "Renewable Energy Systems", "500"),
    ("MCE 504", "Mechatronics System Design", "500"),
    ("MCE 505", "Engineering Project Management", "500"),
]


def _existing_lecturer_id(get_connection, email):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM lecturers WHERE email = ?", (email,)
        ).fetchone()
    return row[0] if row else None


def _existing_course_id(get_connection, lecturer_id, course_code):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM courses WHERE lecturer_id = ? AND course_code = ?",
            (lecturer_id, course_code),
        ).fetchone()
    return row[0] if row else None


def _student_exists(get_connection, lecturer_id, matric_number):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM students WHERE lecturer_id = ? AND matric_number = ?",
            (lecturer_id, matric_number),
        ).fetchone()
    return row is not None


def _print_counts(get_connection):
    tables = ("lecturers", "students", "courses", "enrollments", "attendance")
    counts = {}
    with get_connection() as connection:
        for table in tables:
            counts[table] = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

    print("\nDatabase totals")
    print(f"{'Table':<14} {'Rows':>8}")
    print(f"{'-' * 14} {'-' * 8}")
    for table in tables:
        print(f"{table:<14} {counts[table]:>8}")


def seed_test_data():
    if not os.environ.get("JWT_SECRET_KEY"):
        raise SystemExit(
            "JWT_SECRET_KEY must be set before running this script because "
            "src.auth.auth_manager requires it."
        )

    import numpy as np

    from src.attendance.mark_attendance import mark_attendance
    from src.auth.auth_manager import signup_lecturer
    from src.courses.course_manager import add_course, enroll_student
    from src.database.schema import get_connection, initialize_database
    from src.registration.register_student import save_student

    initialize_database()
    rng = random.Random(RANDOM_SEED)
    embedding_rng = np.random.default_rng(RANDOM_SEED)
    table_names = ("lecturers", "students", "courses", "enrollments", "attendance")
    inserted = {name: 0 for name in table_names}
    skipped = {name: 0 for name in table_names}
    lecturer_records = []

    for lecturer_index, full_name in enumerate(LECTURER_NAMES, start=1):
        email = f"test.lecturer{lecturer_index}@example.com"
        try:
            lecturer_id = signup_lecturer(
                full_name, email, LECTURER_PASSWORD, institution="Test University"
            )
            inserted["lecturers"] += 1
            status = "created"
        except ValueError:
            lecturer_id = _existing_lecturer_id(get_connection, email)
            skipped["lecturers"] += 1
            status = "existing" if lecturer_id is not None else "skipped"

        print(f"Lecturer {status}: id={lecturer_id}, email={email}")
        if lecturer_id is not None:
            lecturer_records.append((lecturer_index, lecturer_id))

    for lecturer_index, lecturer_id in lecturer_records:
        students = []
        for student_index in range(STUDENTS_PER_LECTURER):
            first_name = STUDENT_FIRST_NAMES[student_index % len(STUDENT_FIRST_NAMES)]
            surname_index = (
                student_index // len(STUDENT_FIRST_NAMES) + lecturer_index - 1
            ) % len(STUDENT_LAST_NAMES)
            full_name = f"{first_name} {STUDENT_LAST_NAMES[surname_index]}"
            matric_number = (
                f"AFIT/{20 + student_index % 5}/"
                f"{1000 + (lecturer_index - 1) * STUDENTS_PER_LECTURER + student_index:04d}"
            )
            department = DEPARTMENTS[(student_index + lecturer_index) % len(DEPARTMENTS)]
            level = LEVELS[(student_index // 6) % len(LEVELS)]
            embedding = embedding_rng.normal(size=512).astype(np.float32)

            try:
                save_student(
                    lecturer_id,
                    matric_number,
                    full_name,
                    embedding,
                    department=department,
                    level=level,
                )
                inserted["students"] += 1
            except ValueError:
                skipped["students"] += 1

            if _student_exists(get_connection, lecturer_id, matric_number):
                students.append(matric_number)

        courses = []
        for course_index, (course_code, course_name, level) in enumerate(COURSES):
            try:
                course_id = add_course(
                    lecturer_id,
                    course_code,
                    course_name,
                    department="Mechatronics Engineering",
                    level=level,
                )
                inserted["courses"] += 1
            except ValueError:
                course_id = _existing_course_id(get_connection, lecturer_id, course_code)
                skipped["courses"] += 1

            if course_id is not None:
                courses.append((course_index, course_id))

        if not students:
            print(f"Skipping enrollments and attendance for lecturer {lecturer_id}: no students found")
            continue

        for course_index, course_id in courses:
            start = (course_index * 7 + lecturer_index) % len(students)
            enrolled_students = [
                students[(start + offset) % len(students)]
                for offset in range(min(ENROLLED_PER_COURSE, len(students)))
            ]

            for matric_number in enrolled_students:
                try:
                    enroll_student(lecturer_id, matric_number, course_id)
                    inserted["enrollments"] += 1
                except ValueError:
                    skipped["enrollments"] += 1

            for session_index in range(6):
                session_date = (
                    date.today() - timedelta(days=7 * (5 - session_index))
                ).isoformat()
                present_count = rng.randint(
                    min(5, len(enrolled_students)), min(8, len(enrolled_students))
                )
                present_students = rng.sample(enrolled_students, present_count)
                for matric_number in present_students:
                    result = mark_attendance(
                        lecturer_id, matric_number, course_id, session_date=session_date
                    )
                    if result:
                        inserted["attendance"] += 1
                    else:
                        skipped["attendance"] += 1

    print("\nRun results (new rows / skipped existing rows)")
    for table in table_names:
        print(f"{table:<14} {inserted[table]:>6} / {skipped[table]:<6}")

    _print_counts(get_connection)
    print(f"\nSample login: test.lecturer1@example.com / {LECTURER_PASSWORD}")


if __name__ == "__main__":
    seed_test_data()