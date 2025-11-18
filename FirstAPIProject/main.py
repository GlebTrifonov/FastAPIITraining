from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os

from starlette.responses import HTMLResponse

# 1. СОЗДАНИЕ ПРИЛОЖЕНИЯ
app = FastAPI(
    title="Мой учебный API",
    version="1.0.0",
    description="Этот API создан для изучения FastAPI",
)


# 2. МОДЕЛИ ДАННЫХ
class Student(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int
    email: Optional[str] = None
    is_active: bool = True


class Course(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration_hours: float
    price: float = 0.0
    tags: List[str] = []


class Enrollment(BaseModel):  # Student ---> Course
    id: int
    course_id: int
    student_id: int


# 3. БАЗА ДАННЫХ
students_db = []
courses_db = []
enrollments_db = []

"""""" """""" """""" """HTML PAGE""" """""" """""" """"""


@app.get("/", response_class=HTMLResponse)
async def read_root():
    # learn HTML from templates/index.html
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>HTML file not founded.</h1><p>Create folder templates with file index.html</p>"
        )


@app.get("/students/", response_class=HTMLResponse)
async def students_page():
    try:
        with open("templates/students.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Student page</h1><p>Create folder templates with file students.html</p>"
        )


@app.get("/courses/", response_class=HTMLResponse)
async def courses_page():
    try:
        with open("templates/courses.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Страница курсов</h1><p>HTML файл не найден</p>"
        )


# 4. ЭНДПОИНТЫ ДЛЯ ТЕСТИРОВАНИЯ МОДЕЛЕЙ
@app.get("/")
async def root():
    return {"message": "It's Student Management System"}


@app.post("/api/students/")
async def create_student(student: Student):
    if any(s.id == student.id for s in students_db):
        raise HTTPException(
            status_code=400, detail="Student With This ID Already Exist"
        )

    students_db.append(student)
    return {"message": "Студент создан", "student": student}


@app.get("/api/students/")
async def get_students():
    return {"students": students_db}


@app.get("/api/students/{student_id}")
async def get_student(student_id: int):
    student = next((s for s in students_db if s.id == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student Not Found")

    # Nahodim course
    student_courses = []
    for enrollment in enrollments_db:
        if enrollment.student_id == student.id:
            course = next((c for c in courses_db if c.id == enrollment.course_id), None)
            if course:
                student_courses.append(course)
    return {"student": student, "courses": student_courses}


@app.delete("/api/students/{student_id}")
async def delete_student(student_id: int):
    for student in students_db:
        if student in students_db:
            students_db.remove(student)
    return {"message": "Student deleted successfully"}


# Course Endpoint
@app.post("/api/courses/")
async def crate_course(course: Course):
    if any(c.id == course.id for c in courses_db):
        raise HTTPException(status_code=400, detail="Course With This ID Already Exist")

    courses_db.append(course)
    return {"message": "Course created successfully", "course": course}


@app.get("/api/courses/")
async def get_courses():
    return {"courses": courses_db}


@app.get("/api/courses/{course_id}")
async def get_course(course_id: int):
    course = next((c for c in courses_db if c.id == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course Not Found")

    # Students on course
    course_students = []
    for enrollment in enrollments_db:
        if enrollment.course_id == course_id:
            student = next(
                (s for s in students_db if s.id == enrollment.student_id), None
            )
            if student:
                course_students.append(student)

    return {"course": course, "students": course_students}


@app.delete("/api/courses/{course_id}")
async def delete_course(course_id: int):
    for course in courses_db:
        if course in courses_db:
            courses_db.remove(course)
    return {"message": "Course deleted successfully"}


# Запись на курс
@app.post("/api/enroll/")
async def enroll_student(enrollment: Enrollment):
    # Существование студента
    student = next((s for s in students_db if s.id == enrollment.student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student Not Found")

    # Существование курса
    course = next((c for c in courses_db if c.id == enrollment.course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course Not Found")

    # Записан ли студент на курс
    if any(
        e.student_id == enrollment.student_id and e.course_id == enrollment.course_id
        for e in enrollments_db
    ):
        raise HTTPException(status_code=400, detail="Студент записан на этот курс")
    enrollments_db.append(enrollment)
    return {"message": "Student Enrolled Successfully", "enrollment": enrollment}


@app.get("/api/enrollments/")
async def get_enrollments():
    # ВОзвращаем все записи с информацией
    detailed_enrollments = []
    for enrollment in enrollments_db:
        student = next((s for s in students_db if s.id == enrollment.student_id), None)
        course = next((c for c in courses_db if c.id == enrollment.course_id), None)
        if student and course:
            detailed_enrollments.append(
                {
                    "student": student,
                    "course": course,
                }
            )
    return {"enrollments": detailed_enrollments}
