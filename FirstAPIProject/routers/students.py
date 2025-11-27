from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import crud
from models import Student, StudentCreate
from database import get_db

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/", response_model=list[Student])
async def get_students(db: Session = Depends(get_db)):
    students = crud.get_all_students(db)
    return students


@router.get("/{student_id}", response_model=Student)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=Student)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = crud.create_student(db,student)
    return new_student


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: int, student: StudentCreate, db: Session = Depends(get_db)
):
    updated_student = crud.update_student(db, student_id, student)
    return updated_student


@router.delete("/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}


@router.put("/page/", response_class=HTMLResponse, include_in_schema=False)
async def students_page():
    try:
        with open("templates/students.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Students Page</h1><p>HTML file not found</p>")
