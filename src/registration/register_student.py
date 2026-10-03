import os
import sqlite3
from datetime import datetime, timezone

import cv2
import numpy as np
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.database.schema import get_connection, initialize_database
from src.recognition.face_recognizer import InsightFaceRecognizer, embedding_to_blob
from src.recognition.liveness import is_live_face
from src.utils.config import (
    DEFAULT_CAMERA_INDEX,
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

    frames = []
    try:
        while len(frames) < num_samples:
            ret, frame = capture.read()
            if not ret:
                continue

            faces = recognizer.detect_and_extract(frame)
            display_frame = frame.copy()
            status_text = f"Samples: {len(frames)}/{num_samples}  | SPACE: capture  |  ESC: cancel"
            status_color = (0, 255, 0)
            if len(faces) == 1:
                face = faces[0]
                box = face.bbox.astype(int)
                cv2.rectangle(display_frame,(box[0], box[1]),(box[2], box[3]),(0, 255, 0),2,)

            else:
                face = None
                if len(faces) > 1:
                    status_text = "Multiple faces detected -  only one person allowed"
                    status_color = (0, 0, 255)

            
            cv2.putText(display_frame, status_text, (10, 30),cv2.FONT_HERSHEY_SIMPLEX,0.7, status_color,2)
            cv2.imshow("Register Student", display_frame)

            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                frames = []
                break
            elif key == 32 and len(faces) == 1:

                live, label, score = is_live_face(frame,face.bbox,threshold=liveness_threshold)
                if not live:
                    print(f"[REJECTED] Spoof suspected ({label}, {score:.2f}) - try again.")
                    continue
                frames.append(frame.copy())

    finally:
                capture.release()
                cv2.destroyAllWindows()

    return frames


def generate_embedding(frames):
    recognizer =  InsightFaceRecognizer()
    embeddings = []
    for frame in frames:
        faces = recognizer.detect_and_extract(frame)
        if len(faces) == 1:
            embeddings.append(faces[0].embedding)
    if not embeddings:
        raise ValueError("No valid face embeddings could be extracted from the captured frames")

    return np.mean(embeddings, axis=0)

def save_student(lecturer_id, matric_number, full_name, embedding, department=None,level=None):
    initialize_database()
    registered_at = datetime.now(timezone.utc).isoformat()

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO students (
                    matric_number,
                    lecturer_id,
                    full_name,
                    department,
                    level,
                    embedding,
                    registered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    matric_number,
                    lecturer_id,
                    full_name,
                    department,
                    level,
                    embedding_to_blob(embedding),
                    registered_at,
                ),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(
            f"A student with matric number {matric_number} already exists for this lecturer"
        ) from error


def register_student(lecturer_id,matric_number,full_name,department=None,level=None,camera_index=DEFAULT_CAMERA_INDEX):
    frames = capture_samples(camera_index=camera_index)
    if len(frames) < ENROLLMENT_NUM_SAMPLES:
        raise RuntimeError("Registration cancelled before enough samples were captured")

    embedding = generate_embedding(frames)
    save_student(lecturer_id, matric_number, full_name, embedding, department=department, level=level)


if __name__ == "__main__":
    print("=== Student Registration ===")
    lecturer_id = int(input("Your lecturer id: ").strip())
    matric = input("Enter matric number: ").strip()
    name = input("Enter full name: ").strip()
    department = input("Enter department (optional): ").strip() or None
    lvl = input("Enter level (optional): ").strip() or None

    try:
        register_student(lecturer_id,matric,name,department=department,level=lvl)
        print(f"[SUCCESS] {matric} registered for lecturer {lecturer_id}.")
    except (RuntimeError, ValueError) as error:
        print(f"Registration failed: {error}")
