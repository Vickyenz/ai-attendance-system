from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, courses, students, attendance, reports

app = FastAPI(title="AI Attendance System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your React dev server (Vite default)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"status": "ok"}