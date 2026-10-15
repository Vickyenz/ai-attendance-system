import os
import sys
from typing import Optional
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException
from src.auth.auth_manager import login_lecturer, signup_lecturer

router = APIRouter(prefix="/auth", tags= ["auth"])

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    institution: Optional[str] = None
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/signup", status_code=201)
def signup(payload: SignupRequest):
    try:
        lecturer_id = signup_lecturer(
            payload.full_name, payload.email, payload.password, payload.institution
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"lecturer_id": lecturer_id}

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    try:
        token = login_lecturer(payload.email, payload.password)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))

    return TokenResponse(access_token=token)

