from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import crud
from models import Course, CourseCreate
from database import get_db

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("/", response_model=list[Course])
async def get_courses(db: Session = Depends(get_db)):
    courses = crud.get_all_courses(db)
    return courses

@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.post("/", response_model=Course)
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = crud.create_course(db, course)
    return new_course

@router.put("/{course_id}", response_model=Course)
async def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db)):
    updated_course = crud.update_course(db, course_id, course)

@router.delete("/{course_id}")
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}

@router.get("/page/", response_class=HTMLResponse, include_in_schema=False)
async def courses_page():
    try:
        with open("templates/courses.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Courses Page</h1><p>HTML file not found</p>")