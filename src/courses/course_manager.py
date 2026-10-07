import sqlite3
from datetime import datetime, timezone
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.database.schema import get_connection, initialize_database


def add_course(lecturer_id, course_code, course_name, department=None, level=None):
    """
    Registers a new course. Raises ValueError if the course_code already exists.
    """
    initialize_database()
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO courses (lecturer_id, course_code, course_name, department, level)
                VALUES (?, ?, ?, ?,?)
                """,
                (lecturer_id, course_code, course_name, department, level),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(f"A course with code {course_code} already exists") from error
    return cursor.lastrowid

def get_course_id(lecturer_id, course_code):
    initialize_database()

    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM courses WHERE lecturer_id = ? AND course_code = ?",
            (lecturer_id, course_code),
        ).fetchone()

        if row is None:
            raise ValueError(f"No course with code {course_code} found for this lecturer")

        return row[0]
def enroll_student(lecturer_id, matric_number, course_id):
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
                INSERT INTO enrollments (matric_number, lecturer_id, course_id, enrolled_at)
                VALUES (?, ?, ?, ?)
                """,
                (matric_number, lecturer_id, course_id, enrolled_at),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(
            f"Could not enroll {matric_number} in course {course_id} — "
            f"either already enrolled, or matric_number/course does not belong to this lecturer"
        ) from error
    return True


def is_enrolled(lecturer_id, matric_number, course_id):
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
            WHERE matric_number = ? AND lecturer_id = ? AND course_id = ?
            """,
            (matric_number, lecturer_id, course_id),
        ).fetchone()
    return result is not None


def list_enrolled_students(lecturer_id, course_id):
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
            JOIN students s ON s.matric_number = e.matric_number AND s.lecturer_id = e.lecturer_id
            WHERE e.lecturer_id = ? AND e.course_id = ?
            ORDER BY s.full_name
            """,
            (lecturer_id, course_id),
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


def unenroll_student(lecturer_id, matric_number, course_id):
    """
    Removes a student's enrollment in a course. Returns True if a row was
    actually deleted, False if no matching enrollment existed.
    """
    initialize_database()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM enrollments
            WHERE matric_number = ? AND lecturer_id = ? AND course_id = ?
            """,
            (matric_number, lecturer_id, course_id),
        )
    return cursor.rowcount > 0


def list_courses(lecturer_id):
    """
    Returns all registered courses belonging to this lecturer.
    """
    initialize_database()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, course_code, course_name, department, level 
            FROM courses WHERE lecturer_id =?
            ORDER BY course_code
            """,
            (lecturer_id,),
        ).fetchall()
    return [
        {   
            "id": row[0],
            "course_code": row[1],
            "course_name": row[2],
            "department": row[3],
            "level": row[4],
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

    lecturer_id = int(input("Your lecturer id: ").strip())
    choice = input("Choose an option: ").strip()
    try:
        if choice == "1":
            code = input("Course code: ").strip()
            name = input("Course name: ").strip()
            dept = input("Department (optional): ").strip() or None
            lvl = input("Level (optional): ").strip() or None
            course_id = add_course(lecturer_id, code, name, department=dept, level=lvl)
            print(f"Course {code} with id {course_id} added.")
        elif choice == "2":
            matric = input("Matric number: ").strip()
            code = input("Course code: ").strip()
            course_id = get_course_id(lecturer_id, code)
            enroll_student(lecturer_id, matric, course_id)
            print(f"{matric} enrolled in {code}.")
        elif choice == "3":
            matric = input("Matric number: ").strip()
            code = input("Course code: ").strip()
            course_id = get_course_id(lecturer_id, code)
            enrolled = is_enrolled(lecturer_id, matric, course_id)
            print(f"Enrolled: {enrolled}")
        elif choice == "4":
            code = input("Course code: ").strip()
            course_id = get_course_id(lecturer_id, code)
            students = list_enrolled_students(lecturer_id, course_id)
            for student in students:
                print(f"  {student['matric_number']} — {student['full_name']}")
        elif choice == "5":
            for course in list_courses(lecturer_id):
                print(f" [{course['id']}] {course['course_code']} — {course['course_name']}")
        else:
            print("Invalid option")
    except ValueError as error:
        print(f"Failed: {error}")
