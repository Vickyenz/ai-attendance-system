import sys
import os
import numpy as np
import cv2

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.security import get_current_lecturer_id
from src.recognition.face_recognizer import InsightFaceRecognizer
from src.recognition.liveness import is_live_face
from src.registration.register_student import generate_embedding, save_student
from src.utils.config import LIVENESS_THRESHOLD

router = APIRouter(prefix="/students", tags=["students"])
recognizer = InsightFaceRecognizer()


async def _read_upload_as_frame(file: UploadFile):
    contents = await file.read()
    array = np.frombuffer(contents, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode image")
    return frame


@router.post("/register", status_code=201)
async def register_student_endpoint(
    matric_number: str = Form(...),
    full_name: str = Form(...),
    department: Optional[str] = Form(None),
    level: Optional[str] = Form(None),
    samples: list[UploadFile] = File(...),
    lecturer_id: int = Depends(get_current_lecturer_id),
):
    """
    Accepts multiple captured frames (sent as files) from the browser,
    runs the same liveness + embedding pipeline as the CLI version.
    """
    accepted_frames = []

    for upload in samples:
        frame = await _read_upload_as_frame(upload)
        faces = recognizer.detect_and_extract(frame)

        if len(faces) != 1:
            continue  # skip frames with zero or multiple faces

        live, label, score = is_live_face(frame, faces[0].bbox, threshold=LIVENESS_THRESHOLD)
        if live:
            accepted_frames.append(frame)

    if not accepted_frames:
        raise HTTPException(status_code=400, detail="No valid, live face samples found")

    embedding = generate_embedding(accepted_frames)

    try:
        save_student(lecturer_id, matric_number, full_name, embedding, department, level)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "registered", "matric_number": matric_number, "samples_used": len(accepted_frames)}