import sys
import os
import numpy as np
import cv2

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.security import get_current_lecturer_id
from src.recognition.face_recognizer import InsightFaceRecognizer, load_known_embeddings, match_face
from src.recognition.liveness import is_live_face
from src.courses.course_manager import is_enrolled
from src.attendance.mark_attendance import mark_attendance, list_attendance
from src.utils.config import LIVENESS_THRESHOLD, RECOGNITION_THRESHOLD

router = APIRouter(prefix="/attendance", tags=["attendance"])
recognizer = InsightFaceRecognizer()


@router.post("/{course_id}/recognize")
async def recognize_frame(
    course_id: int,
    frame_file: UploadFile = File(...),
    lecturer_id: int = Depends(get_current_lecturer_id),
):
    """
    Accepts ONE frame from the browser's live camera feed, runs the full
    liveness -> recognition -> enrollment -> attendance pipeline on every
    face found, and returns a result per face — this is what the browser
    calls repeatedly (e.g. every second) during a live session.
    """
    contents = await frame_file.read()
    array = np.frombuffer(contents, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode image")

    known_embeddings = load_known_embeddings(lecturer_id)
    faces = recognizer.detect_and_extract(frame)
    results = []

    for face in faces:
        box = face.bbox.astype(int).tolist()

        live, label, score = is_live_face(frame, face.bbox, threshold=LIVENESS_THRESHOLD)
        if not live:
            results.append({"box": box, "status": "spoof", "label": label, "score": score})
            continue

        best_match, match_score = match_face(face.embedding, known_embeddings, threshold=RECOGNITION_THRESHOLD)
        if best_match == "Unknown":
            results.append({"box": box, "status": "unknown", "score": match_score})
            continue

        if not is_enrolled(lecturer_id, best_match, course_id):
            results.append({"box": box, "status": "not_enrolled", "matric_number": best_match})
            continue

        marked = mark_attendance(lecturer_id, best_match, course_id)
        results.append({
            "box": box,
            "status": "marked" if marked else "already_marked",
            "matric_number": best_match,
            "score": match_score,
        })

    return {"faces": results}


@router.get("/{course_id}")
def get_attendance(course_id: int, session_date: Optional[str] = None, lecturer_id: int = Depends(get_current_lecturer_id)):
    return list_attendance(lecturer_id, course_id=course_id, session_date=session_date)