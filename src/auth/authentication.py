import os
import sys
import sqlite3
import logging
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.database.schema import get_connection, initialize_database
from email_validator import validate_email, EmailNotValidError
logger = logging.getLogger(__name__)
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
MIN_PASSWORD_LENGTH = 8

def validate_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"PAssword must be at least {MIN_PASSWORD_LENGTH} characters")
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password is too long")


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password, password_hash):
    pw = password.encode("utf-8")
    if len(pw) > 72:
        return False
    return bcrypt.checkpw(pw, password_hash.encode("utf-8"))

def create_access_token(lecturer_id):
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(lecturer_id), "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        return int(payload["sub"])

    except (jwt.PyJWTError, KeyError, ValueError):
        return None

def signup_lecturer(full_name, email, password, institution=None):
    if not all(isinstance(v, str) for v in (full_name, email, password)):
        raise ValueError("Full name, email and password are required")

    full_name = full_name.strip()
    email = email.strip().lower()
    institution = institution.strip() or None if isinstance(institution, str) else None


    if not full_name:
        raise ValueError("Full name is required")

    try:
        email = validate_email(email, check_deliverability=True).normalized

    except EmailNotValidError as error:
        raise ValueError(f"Invalid email:{error}") from error
   
    validate_password(password)
    try:
        initialize_database()
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO lecturers (full_name,, email, password_hash, institution, created_at)
                VALUES (?,?,?,?,?)"""
                (full_name.strip(), email, hash_password(password), institution, datetime.now(timezone.utc).isoformat()),
            )

            

    except sqlite3.IntegrityError as error:
        message = str(error).lower()
        if "unique" in message and "email" in message:
            raise ValueError(f"An account with email {email} already exists") from error
        if "not null" in message:
            raise ValueError("A required field is missing") from error
        logger.exception("Unexpected integrity error during signup")
        raise ValueError("Could not create the account with the details given") from error

    except sqlite3.OperationalError as error:
        logger.exception("Database operational error during signup")
        raise RuntimeError("The database is busy or unavailable. Please try again.") from error

    except sqlite3.DatabaseError as error:
        logger.exception("Database error during signup")
        raise RuntimeError("A database error occurred. Please try again.") from error


    return cursor.lastrowid


def login_lecturer(email, password):
    initialize_database()
    email = email.strip().lower()

    with get_connection as connection:
        row = connection.execute(
            "SELECT id, password_hash FROM lecturers WHERE email = ?", (email,)
        ).fetchone()

    if row is None or not verify_password(password, row[1]):
        raise ValueError("Invalid email or password")

    return create_access_token(row[0])

def get_lecturer_by_id(lecturer_id):
    initialize_database()
    with get_connection as connection:
        row = connection.execute(
            "SELECT id, full_name, email, institution FROM lecturers WHERE id = ?", (lecturer_id,),
        ).fetchone()

        if row is None:
            return None

        return {"id": row[0], "full_name": row[1], "email": row[2], "institution": row[3]}

if __name__ == "__main__":
    print("1. Sign up\n2. Log in")
    choice = input("choose: ").strip()
    try:
        if choice == "1":
            lid = signup_lecturer(input("Full name: "), input("Email: "), input("Password: "), input("Institution: ") or None)
            print(f"Account created with id {lid}")

        elif choice == "2":
            token = login_lecturer(input("Email: "), input("Password"))
            print(f"Token: {token}")
            print(f"Decoded lecturer id: {decode_access_token(token)}")

    except ValueError as error:
        print(f"Failed: {error}")