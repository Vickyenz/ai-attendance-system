import sqlite3
import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.courses.course_manager import is_enrolled
from src.database.schema import get_connection, initialize_database


def _normalize_session_date(session_date=None):
    if session_date is None:
        return datetime.now(timezone.utc).date().isoformat()

    if isinstance(session_date, datetime):
        return session_date.date().isoformat()

    if isinstance(session_date, str):
        cleaned = session_date.strip()
        if not cleaned:
            raise ValueError("Session date cannot be empty")
        try:
            return datetime.fromisoformat(cleaned).date().isoformat()
        except ValueError:
            try:
                return datetime.strptime(cleaned, "%Y-%m-%d").date().isoformat()
            except ValueError as error:
                raise ValueError(f"Invalid session date: {session_date}") from error

    raise ValueError("session_date must be a date string, ISO datetime, or None")


def mark_attendance(matric_number, course_code, session_date=None):
    """
    Records attendance for a student in a course on a given session date.
    If attendance has already been recorded, the function silently returns False
    so the caller can skip the student without raising an error.
    Raises ValueError only when the student is not enrolled in the course.
    """
    initialize_database()
    normalized_date = _normalize_session_date(session_date)

    if not is_enrolled(matric_number, course_code):
        raise ValueError(
            f"Cannot mark attendance: {matric_number} is not enrolled in {course_code}"
        )

    if is_attendance_marked(matric_number, course_code, normalized_date):
        return False

    recorded_at = datetime.now(timezone.utc).isoformat()
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO attendance (matric_number, course_code, session_date, recorded_at)
                VALUES (?, ?, ?, ?)
                """,
                (matric_number, course_code, normalized_date, recorded_at),
            )
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return False


def is_attendance_marked(matric_number, course_code, session_date=None):
    """
    Returns True if attendance has already been recorded for the student/course/date.
    """
    initialize_database()
    normalized_date = _normalize_session_date(session_date)
    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT 1 FROM attendance
            WHERE matric_number = ? AND course_code = ? AND session_date = ?
            """,
            (matric_number, course_code, normalized_date),
        ).fetchone()
    return result is not None


def list_attendance(course_code=None, session_date=None):
    """
    Returns attendance rows as a list of dictionaries.
    When course_code is provided, only that course is included.
    When session_date is provided, only that session date is included.
    """
    initialize_database()
    normalized_date = _normalize_session_date(session_date) if session_date is not None else None

    if course_code is not None and normalized_date is not None:
        query = """
            SELECT a.matric_number, s.full_name, s.department, s.level,
                   a.course_code, a.session_date, a.recorded_at
            FROM attendance a
            JOIN students s ON s.matric_number = a.matric_number
            WHERE a.course_code = ? AND a.session_date = ?
            ORDER BY s.full_name
        """
        params = (course_code, normalized_date)
    elif course_code is not None:
        query = """
            SELECT a.matric_number, s.full_name, s.department, s.level,
                   a.course_code, a.session_date, a.recorded_at
            FROM attendance a
            JOIN students s ON s.matric_number = a.matric_number
            WHERE a.course_code = ?
            ORDER BY a.session_date DESC, s.full_name
        """
        params = (course_code,)
    elif normalized_date is not None:
        query = """
            SELECT a.matric_number, s.full_name, s.department, s.level,
                   a.course_code, a.session_date, a.recorded_at
            FROM attendance a
            JOIN students s ON s.matric_number = a.matric_number
            WHERE a.session_date = ?
            ORDER BY a.course_code, s.full_name
        """
        params = (normalized_date,)
    else:
        query = """
            SELECT a.matric_number, s.full_name, s.department, s.level,
                   a.course_code, a.session_date, a.recorded_at
            FROM attendance a
            JOIN students s ON s.matric_number = a.matric_number
            ORDER BY a.session_date DESC, a.course_code, s.full_name
        """
        params = ()

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        {
            "matric_number": row[0],
            "full_name": row[1],
            "department": row[2],
            "level": row[3],
            "course_code": row[4],
            "session_date": row[5],
            "recorded_at": row[6],
        }
        for row in rows
    ]


def list_student_attendance(matric_number):
    """
    Returns all attendance records for a specific student.
    """
    initialize_database()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT a.course_code, c.course_name, a.session_date, a.recorded_at
            FROM attendance a
            JOIN courses c ON c.course_code = a.course_code
            WHERE a.matric_number = ?
            ORDER BY a.session_date DESC, a.course_code
            """,
            (matric_number,),
        ).fetchall()

    return [
        {
            "course_code": row[0],
            "course_name": row[1],
            "session_date": row[2],
            "recorded_at": row[3],
        }
        for row in rows
    ]


if __name__ == "__main__":
    print("=== Attendance Manager (CLI test) ===")
    print("1. Mark attendance")
    print("2. Check attendance")
    print("3. List attendance for a course")
    print("4. List all attendance")
    choice = input("Choose an option: ").strip()

    try:
        if choice == "1":
            matric = input("Matric number: ").strip()
            course = input("Course code: ").strip()
            session = input("Session date (YYYY-MM-DD, optional): ").strip() or None
            row_id = mark_attendance(matric, course, session_date=session)
            print(f"Attendance recorded with id {row_id}")
        elif choice == "2":
            matric = input("Matric number: ").strip()
            course = input("Course code: ").strip()
            session = input("Session date (YYYY-MM-DD, optional): ").strip() or None
            marked = is_attendance_marked(matric, course, session_date=session)
            print(f"Attendance marked: {marked}")
        elif choice == "3":
            course = input("Course code: ").strip()
            session = input("Session date (YYYY-MM-DD, optional): ").strip() or None
            for entry in list_attendance(course_code=course, session_date=session):
                print(f"  {entry['matric_number']} — {entry['full_name']} — {entry['session_date']}")
        elif choice == "4":
            for entry in list_attendance():
                print(
                    f"  {entry['matric_number']} | {entry['course_code']} | {entry['session_date']}"
                )
        else:
            print("Invalid option")
    except ValueError as error:
        print(f"Failed: {error}")
