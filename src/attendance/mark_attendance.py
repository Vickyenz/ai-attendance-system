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


def mark_attendance(lecturer_id, matric_number, course_id, session_date=None):
    """
    Records attendance for a student in a course on a given session date.
    If attendance has already been recorded, the function silently returns False
    so the caller can skip the student without raising an error.
    Raises ValueError only when the student is not enrolled in the course.
    """
    initialize_database()
    normalized_date = _normalize_session_date(session_date)

    if not is_enrolled(lecturer_id, matric_number, course_id):
        raise ValueError(
            f"Cannot mark attendance: {matric_number} is not enrolled in {course_id}"
        )

    if is_attendance_marked(lecturer_id, matric_number, course_id, normalized_date):
        return False

    recorded_at = datetime.now(timezone.utc).isoformat()
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO attendance (matric_number, lecturer_id, course_id, session_date, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (matric_number, lecturer_id, course_id, normalized_date, recorded_at),
            )
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return False


def is_attendance_marked(lecturer_id, matric_number, course_id, session_date):
    """
    Returns True if attendance has already been recorded for the student/course/date.
    """
    initialize_database()
    normalized_date = _normalize_session_date(session_date)
    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT 1 FROM attendance
            WHERE matric_number = ? AND lecturer_id =? AND course_id = ? AND session_date = ?
            """,
            (matric_number,lecturer_id, course_id, normalized_date),
        ).fetchone()
    return result is not None


def list_attendance(lecturer_id, course_id=None, session_date=None):
    """
    Returns attendance rows as a list of dictionaries.
    When course_code is provided, only that course is included.
    When session_date is provided, only that session date is included.
    """
    initialize_database()
    normalized_date = _normalize_session_date(session_date) if session_date is not None else None

    base_select = """
            SELECT a.matric_number, s.full_name, s.department, s.level,
                    a.course_id, c.course_code, a.session_date, a.recorded_at
            FROM attendance a
            JOIN students s ON s.matric_number = a.matric_number AND s.lecturer_id = a.lecturer_id
            JOIN courses c ON c.id = a.course_id AND c.lecturer_id = a.lecturer_id
            WHERE a.lecturer_id = ?
    """
    params = [lecturer_id]
    if course_id is not None:
        base_select += " AND a.course_id = ?"
        params.append(course_id)

    if normalized_date is not None:
        base_select += " AND a.session_date = ?"
        params.append(normalized_date)

    base_select += " ORDER BY a.session_date DESC, c.course_code, s.full_name"
    with get_connection() as connection:
        rows = connection.execute(base_select, params).fetchall()

    return [
        {
            "matric_number": row[0],
            "full_name": row[1],
            "department": row[2],
            "level": row[3],
            "course_id": row[4],
            "course_code": row[5],
            "session_date": row[6],
            "recorded_at": row[7],
        }
        for row in rows
    ]


def list_student_attendance(lecturer_id, matric_number):
    """
    Returns all attendance records for a specific student.
    """
    initialize_database()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT a.course_id, c.course_code, c.course_name, a.session_date, a.recorded_at
            FROM attendance a
            JOIN courses c ON c.id = a.course_id AND c.lecturer_id = a.lecturer_id
            WHERE a.matric_number = ? AND a.lecturer_id = ?
            ORDER BY a.session_date DESC, a.course_code
            """,
            (matric_number,lecturer_id),
        ).fetchall()

    return [
        {
            "course_id": row[0],
            "course_code": row[1],
            "course_name": row[2],
            "session_date": row[3],
            "recorded_at": row[4],
        }
        for row in rows
    ]


if __name__ == "__main__":
    print("=== Attendance Manager (CLI test) ===")
    print("1. Mark attendance")
    print("2. Check attendance")
    print("3. List attendance for a course")
    print("4. List all attendance")

    lecturer_id = int(input("Your lecturer id: ").strip())
    choice = input("Choose an option: ").strip()

    try:
        if choice == "1":
            matric = input("Matric number: ").strip()
            course_id = int(input("Course id: ").strip())
            session = input("Session date (YYYY-MM-DD, optional): ").strip() or None
            result = mark_attendance(lecturer_id, matric, course_id, session_date=session)
            print(f"Attendance recorded with id {result}" if result else "Already marked")
        elif choice == "2":
            matric = input("Matric number: ").strip()
            course_id = int(input("Course id: ").strip())
            session = input("Session date (YYYY-MM-DD, optional): ").strip() or None
            marked = is_attendance_marked(lecturer_id, matric, course_id, session_date=session)
            print(f"Attendance marked: {marked}")
        elif choice == "3":
            course_id = int(input("Course id: ").strip())
            session = input("Session date (YYYY-MM-DD, optional): ").strip() or None
            for entry in list_attendance(lecturer_id, course_id=course_id, session_date=session):
                print(f"  {entry['matric_number']} — {entry['full_name']} — {entry['session_date']}")
        elif choice == "4":
            for entry in list_attendance(lecturer_id):
                print(
                    f"  {entry['matric_number']} | {entry['course_code']} | {entry['session_date']}"
                )
        else:
            print("Invalid option")
    except ValueError as error:
        print(f"Failed: {error}")
