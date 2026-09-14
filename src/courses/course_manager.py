import sqlite3
from datetime import datetime, timezone
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.database.schema import get_connection, initialize_database


def add_course(course_code, course_name, department=None, level=None):
    """
    Registers a new course. Raises ValueError if the course_code already exists.
    """
    initialize_database()
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO courses (course_code, course_name, department, level)
                VALUES (?, ?, ?, ?)
                """,
                (course_code, course_name, department, level),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(f"A course with code {course_code} already exists") from error
    return course_code


def enroll_student(matric_number, course_code):
    """
    Links a student to a course. Raises ValueError if the student or course
    doesn't exist (foreign key violation) or if the student is already
    enrolled in this course (primary key violation).
    """
    initialize_database()
    enrolled_at = datetime.now(timezone.utc).isoformat()
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO enrollments (matric_number, course_code, enrolled_at)
                VALUES (?, ?, ?)
                """,
                (matric_number, course_code, enrolled_at),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(
            f"Could not enroll {matric_number} in {course_code} — "
            f"either already enrolled, or matric_number/course_code does not exist"
        ) from error
    return True


def is_enrolled(matric_number, course_code):
    """
    Returns True if the student is enrolled in the given course, False otherwise.
    This is the gate check the attendance module will call before logging
    an attendance record.
    """
    initialize_database()
    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT 1 FROM enrollments
            WHERE matric_number = ? AND course_code = ?
            """,
            (matric_number, course_code),
        ).fetchone()
    return result is not None


def list_enrolled_students(course_code):
    """
    Returns a list of dicts, one per student enrolled in the given course,
    joining in name/department/level from the students table. Useful for
    reports and lecturer-side sanity checks.
    """
    initialize_database()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT s.matric_number, s.full_name, s.department, s.level, e.enrolled_at
            FROM enrollments e
            JOIN students s ON s.matric_number = e.matric_number
            WHERE e.course_code = ?
            ORDER BY s.full_name
            """,
            (course_code,),
        ).fetchall()
    return [
        {
            "matric_number": row[0],
            "full_name": row[1],
            "department": row[2],
            "level": row[3],
            "enrolled_at": row[4],
        }
        for row in rows
    ]


def unenroll_student(matric_number, course_code):
    """
    Removes a student's enrollment in a course. Returns True if a row was
    actually deleted, False if no matching enrollment existed.
    """
    initialize_database()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM enrollments
            WHERE matric_number = ? AND course_code = ?
            """,
            (matric_number, course_code),
        )
    return cursor.rowcount > 0


def list_courses():
    """
    Returns all registered courses as a list of dicts.
    """
    initialize_database()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT course_code, course_name, department, level FROM courses ORDER BY course_code"
        ).fetchall()
    return [
        {
            "course_code": row[0],
            "course_name": row[1],
            "department": row[2],
            "level": row[3],
        }
        for row in rows
    ]


if __name__ == "__main__":
    print("=== Course Manager (CLI test) ===")
    print("1. Add course")
    print("2. Enroll student")
    print("3. Check enrollment")
    print("4. List enrolled students")
    print("5. List all courses")
    choice = input("Choose an option: ").strip()
    try:
        if choice == "1":
            code = input("Course code: ").strip()
            name = input("Course name: ").strip()
            dept = input("Department (optional): ").strip() or None
            lvl = input("Level (optional): ").strip() or None
            add_course(code, name, department=dept, level=lvl)
            print(f"Course {code} added.")
        elif choice == "2":
            matric = input("Matric number: ").strip()
            code = input("Course code: ").strip()
            enroll_student(matric, code)
            print(f"{matric} enrolled in {code}.")
        elif choice == "3":
            matric = input("Matric number: ").strip()
            code = input("Course code: ").strip()
            enrolled = is_enrolled(matric, code)
            print(f"Enrolled: {enrolled}")
        elif choice == "4":
            code = input("Course code: ").strip()
            students = list_enrolled_students(code)
            for student in students:
                print(f"  {student['matric_number']} — {student['full_name']}")
        elif choice == "5":
            for course in list_courses():
                print(f"  {course['course_code']} — {course['course_name']}")
        else:
            print("Invalid option")
    except ValueError as error:
        print(f"Failed: {error}")
