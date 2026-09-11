import sqlite3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    matric_number TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    department TEXT,
    level TEXT,
    embedding_path TEXT NOT NULL,
    registered_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    course_code TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    department TEXT,
    level TEXT
);

CREATE TABLE IF NOT EXISTS enrollments (
    matric_number TEXT NOT NULL,
    course_code TEXT NOT NULL,
    enrolled_at TEXT NOT NULL,
    PRIMARY KEY (matric_number, course_code),
    FOREIGN KEY (matric_number) REFERENCES students(matric_number),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matric_number TEXT NOT NULL,
    course_code TEXT NOT NULL,
    session_date TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE (matric_number, course_code, session_date),
    FOREIGN KEY (matric_number) REFERENCES students(matric_number),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
);
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
