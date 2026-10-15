import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from app.security import get_current_lecturer_id
from src.reports.export_attendance import export_attendance

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/export")
def export(course_id: Optional[int] = None, session_date: Optional[str] = None , lecturer_id: int = Depends(get_current_lecturer_id)):
    try:
        path = export_attendance(lecturer_id, course_id=course_id, session_date=session_date)
    except RuntimeError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(path),
    )