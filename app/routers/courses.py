import sys
import os
from pydantic import BaseModel
from typing import Optional
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from fastapi import APIRouter, HTTPException, Depends
from app.security import get_current_lecturer_id
from src.courses.course_manager import (
    add_course, enroll_student, is_enrolled,
    list_enrolled_students, unenroll_student, list_courses, get_course_id,
)

router = APIRouter(prefix="/courses", tags=["courses"])

class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    department: Optional[str] = None
    level: Optional[str] = None

class EnrollRequest(BaseModel):
    matric_number: str


@router.get("")
def get_courses(lecturer_id: int = Depends(get_current_lecturer_id)):
    return list_courses(lecturer_id)

@router.post("")
def create_course(payload: CourseCreate, lecturer_id: int = Depends(get_current_lecturer_id)):
    try:
        course_id = add_course(lecturer_id, payload.course_code, payload.course_name, payload.department, payload.level)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"course_id": course_id}

@router.post("/{course_id}/enroll", status_code=201)
def enroll(course_id: int, payload: EnrollRequest, lecturer_id: int = Depends(get_current_lecturer_id)):
    try:
        enroll_student(lecturer_id, payload.matric_number, course_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "enrolled"}

@router.get("/{course_id}/students")
def get_enrolled_students(course_id: int, lecturer_id: int = Depends(get_current_lecturer_id)):
    return list_enrolled_students(lecturer_id, course_id)

@router.delete("/{course_id}/students/{matric_number:path}")
def unenroll(course_id: int, matric_number: str, lecturer_id: int = Depends(get_current_lecturer_id)):
    removed = unenroll_student(lecturer_id, matric_number, course_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"status": "unenrolled"}