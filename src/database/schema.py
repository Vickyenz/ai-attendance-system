import sqlite3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.config import DB_PATH


SCHEMA = """
CREATE TABLE lecturers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    institution TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE students (
    matric_number TEXT NOT NULL,
    lecturer_id INTEGER NOT NULL REFERENCES lecturers(id),
    full_name TEXT NOT NULL,
    department TEXT,
    level TEXT,
    embedding BLOB NOT NULL,
    registered_at TEXT NOT NULL,
    PRIMARY KEY (matric_number, lecturer_id)
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id INTEGER NOT NULL REFERENCES lecturers(id),
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    department TEXT,
    level TEXT,
    UNIQUE (lecturer_id, course_code),
    UNIQUE (id, lecturer_id)
);

CREATE TABLE IF NOT EXISTS enrollments (
    matric_number TEXT NOT NULL,
    lecturer_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TEXT NOT NULL,
    PRIMARY KEY (matric_number, lecturer_id, course_id),
    FOREIGN KEY (matric_number, lecturer_id)
        REFERENCES students (matric_number, lecturer_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id, lecturer_id)
        REFERENCES courses (id, lecturer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matric_number TEXT NOT NULL,
    lecturer_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    session_date TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE (matric_number, lecturer_id, course_id, session_date),
    FOREIGN KEY (matric_number, lecturer_id)
        REFERENCES students (matric_number, lecturer_id),
    FOREIGN KEY (course_id, lecturer_id)
        REFERENCES courses (id, lecturer_id)
);

CREATE INDEX IF NOT EXISTS idx_students_lecturer ON students (lecturer_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments (course_id);
CREATE INDEX IF NOT EXISTS idx_attendance_course_date ON attendance (course_id, session_date);
"""


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript(SCHEMA)


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DB_PATH}")
