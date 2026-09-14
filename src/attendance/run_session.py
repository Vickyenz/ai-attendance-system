"""
src/attendance/run_session.py

Live attendance session orchestrator — this is the actual classroom-facing
entry point matching the project proposal's workflow:

    1. Lecturer selects course and starts session
    2. Webcam captures faces continuously
    3. Each detected face passes through: liveness check -> recognition -> enrollment check -> attendance marking
    4. Duplicate entries prevented (both in-session, via a local cache, and
       at the DB level via mark_attendance()'s existing UNIQUE constraint backstop)

This script is intentionally a thin orchestration layer — all real logic
(recognition, liveness, enrollment, attendance persistence) lives in the
existing modules it imports. Nothing here should reimplement logic that
already exists elsewhere in the codebase.
"""

import sys
import os
import cv2

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.recognition.face_recognizer import (
    InsightFaceRecognizer,
    load_known_embeddings,
    match_face,
)
from src.recognition.liveness import is_live_face
from src.courses.course_manager import is_enrolled, list_courses
from src.attendance.mark_attendance import mark_attendance, is_attendance_marked
from src.utils.config import RECOGNITION_THRESHOLD, LIVENESS_THRESHOLD, DEFAULT_CAMERA_INDEX


def run_session(course_code, session_date=None, camera_index=DEFAULT_CAMERA_INDEX):
    """
    Runs a live attendance session for the given course. Opens the webcam,
    recognizes enrolled students, checks liveness, and marks attendance —
    each student only counted once per session (tracked locally to avoid
    redundant DB checks every frame, though mark_attendance() remains the
    real source of truth and would catch any duplicate regardless).

    Press 'q' to end the session.
    """
    recognizer = InsightFaceRecognizer()
    known_embeddings = load_known_embeddings()

    if not known_embeddings:
        print("[ERROR] No enrolled students found in embeddings directory.")
        return

    print(f"[INFO] Loaded {len(known_embeddings)} known face(s).")
    print(f"[INFO] Starting session for course: {course_code}")

    # Local cache so we don't re-query the DB every single frame for a
    # student who's still sitting in view after being marked.
    already_processed_this_session = set()

    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        faces = recognizer.detect_and_extract(frame)

        for face in faces:
            box = face.bbox.astype(int)

            # ── Stage 1: Liveness ───────────────────────────────────
            live, spoof_label, spoof_score = is_live_face(frame, face.bbox, threshold=LIVENESS_THRESHOLD)
            if not live:
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                cv2.putText(frame, f"SPOOF ({spoof_score:.2f})", (box[0], box[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                continue

            # ── Stage 2: Recognition ────────────────────────────────
            best_match, best_score = match_face(face.embedding, known_embeddings, threshold=RECOGNITION_THRESHOLD)

            if best_match == "Unknown":
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (box[0], box[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                continue

            # ── Stage 3: Enrollment + Attendance ────────────────────
            status_text = ""
            status_color = (0, 255, 0)

            if best_match in already_processed_this_session:
                status_text = f"{best_match} — already checked in"
                status_color = (0, 255, 255)  # yellow
            else:
                if not is_enrolled(best_match, course_code):
                    status_text = f"{best_match} — NOT ENROLLED in {course_code}"
                    status_color = (0, 0, 255)
                else:
                    result = mark_attendance(best_match, course_code, session_date=session_date)
                    already_processed_this_session.add(best_match)

                    if result is False:
                        status_text = f"{best_match} — already marked"
                        status_color = (0, 255, 255)
                    else:
                        status_text = f"{best_match} — ATTENDANCE MARKED"
                        status_color = (0, 255, 0)
                        print(f"[MARKED] {best_match} — {course_code}")

            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), status_color, 2)
            cv2.putText(frame, status_text, (box[0], box[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

        cv2.putText(frame, f"Course: {course_code} | Marked: {len(already_processed_this_session)} | 'q' to end session",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Attendance Session", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n[SESSION ENDED] {len(already_processed_this_session)} student(s) processed for {course_code}.")


if __name__ == "__main__":
    print("=== Start Attendance Session ===")
    courses = list_courses()

    if not courses:
        print("[ERROR] No courses registered. Add a course first.")
        sys.exit(1)

    print("Available courses:")
    for c in courses:
        print(f"  {c['course_code']} — {c['course_name']}")

    code = input("\nEnter course code to start session: ").strip()
    date_input = input("Session date (YYYY-MM-DD, leave blank for today): ").strip() or None

    run_session(code, session_date=date_input)