import os
import sqlite3
from datetime import datetime, timezone

import cv2
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.database.schema import get_connection, initialize_database
from src.recognition.face_recognizer import InsightFaceRecognizer
from src.recognition.liveness import is_live_face
from src.utils.config import (
    DEFAULT_CAMERA_INDEX,
    EMBEDDINGS_DIR,
    ENROLLMENT_NUM_SAMPLES,
    LIVENESS_THRESHOLD,
)


def capture_samples(
    camera_index=DEFAULT_CAMERA_INDEX,
    num_samples=ENROLLMENT_NUM_SAMPLES,
    liveness_threshold=LIVENESS_THRESHOLD,
):
    recognizer = InsightFaceRecognizer()
    capture = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open camera index {camera_index}")

    embeddings = []
    try:
        while len(embeddings) < num_samples:
            ret, frame = capture.read()
            if not ret:
                continue

            faces = recognizer.detect_and_extract(frame)
            if len(faces) == 1:
                face = faces[0]
                box = face.bbox.astype(int)
                live, label, score = is_live_face(
                    frame,
                    face.bbox,
                    threshold=liveness_threshold,
                )
                color = (0, 255, 0) if live else (0, 0, 255)
                message = (
                    f"Samples: {len(embeddings)} / {num_samples}"
                    if live
                    else f"REJECTED: {label} {score:.2f}"
                )

                cv2.rectangle(
                    frame,
                    (box[0], box[1]),
                    (box[2], box[3]),
                    color,
                    2,
                )
                cv2.putText(
                    frame,
                    message,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                )

                if live:
                    embeddings.append(face.embedding.copy())

            cv2.imshow("Student Registration", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()

    return embeddings


def generate_embedding(sample_embeddings):
    if not sample_embeddings:
        raise ValueError("At least one face embedding is required")

    embeddings = np.asarray(sample_embeddings, dtype=np.float32)
    if embeddings.ndim != 2:
        raise ValueError("Sample embeddings must be a two-dimensional array")

    return np.mean(embeddings, axis=0)


def save_student(
    matric_number,
    full_name,
    embedding,
    department=None,
    level=None,
):
    initialize_database()
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    embedding_path = os.path.join(EMBEDDINGS_DIR, f"{matric_number}.npy")
    registered_at = datetime.now(timezone.utc).isoformat()
    np.save(embedding_path, np.asarray(embedding, dtype=np.float32))

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO students (
                    matric_number,
                    full_name,
                    department,
                    level,
                    embedding_path,
                    registered_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    matric_number,
                    full_name,
                    department,
                    level,
                    embedding_path,
                    registered_at,
                ),
            )
    except sqlite3.IntegrityError as error:
        if os.path.exists(embedding_path):
            os.remove(embedding_path)
        raise ValueError(
            f"A student with matric number {matric_number} already exists"
        ) from error

    return embedding_path


def register_student(
    matric_number,
    full_name,
    department=None,
    level=None,
    camera_index=DEFAULT_CAMERA_INDEX,
):
    samples = capture_samples(camera_index=camera_index)
    if len(samples) < ENROLLMENT_NUM_SAMPLES:
        raise RuntimeError("Registration cancelled before enough samples were captured")

    embedding = generate_embedding(samples)
    return save_student(
        matric_number,
        full_name,
        embedding,
        department=department,
        level=level,
    )


if __name__ == "__main__":
    student_matric = input("Enter matric number: ").strip()
    student_name = input("Enter full name: ").strip()
    student_department = input("Enter department (optional): ").strip() or None
    student_level = input("Enter level (optional): ").strip() or None

    try:
        path = register_student(
            student_matric,
            student_name,
            department=student_department,
            level=student_level,
        )
        print(f"Registration complete. Embedding saved to {path}")
    except (RuntimeError, ValueError) as error:
        print(f"Registration failed: {error}")
