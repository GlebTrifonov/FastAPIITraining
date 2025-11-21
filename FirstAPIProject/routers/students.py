from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import crud
from models import Student, StudentCreate

router = APIRouter(prefix="/api/students", tags=["students"])

@router.get("/", response_model=list[Student])
async def get_students():
    students = crud.get_all_students()
    return students

@router.get("/{student_id}", response_model=Student)
async def get_student(student_id: int):
    student = crud.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/", response_model=Student)
async def create_student(student: StudentCreate):
    new_student = crud.create_student(student)
    return new_student

@router.delete("/{student_id}")
async def delete_student(student_id: int):
    success = crud.delete_student(student_id)
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
