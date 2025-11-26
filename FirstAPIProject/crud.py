from http.client import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select
from database import Student, Course, Enrollment, get_db
from models import StudentCreate, CourseCreate, EnrollmentCreate

def create_student(db: Session, student: StudentCreate) -> Student:
    db_student = Student(
        first_name=student.first_name,
        last_name=student.last_name,
        age=student.age,
        email=student.email,
        is_active=student.is_active,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)

def get_all_students(db: Session) -> list[Student]:
    result = db.execute(select(Student))
    return result.scalars().all()

def update_student(db: Session, student_id: int, student_data:StudentCreate) -> Student:
    db_student = db.get(db, student_id)
    db_student.first_name = student_data.first_name
    db_student.last_name = student_data.last_name
    db_student.age = student_data.age
    db_student.email = student_data.email
    db_student.is_active = student_data.is_active
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int) -> bool:
    student = db.get(Student, student_id)
    if student:
        db.delete(student)
        db.commit()
        return True
    return False

def create_course(db:Session, course: CourseCreate) -> Course:
    db_course = Course(
        title=course.title,
        description=course.description,
        duration_hours=course.duration_hours,
        price=course.price,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)

def get_all_courses(db: Session) -> list[Course]:
    result = db.execute(select(Course))
    return result.scalars().all()

def update_course(db: Session, course_id: int, course_data: CourseCreate) -> Course:
    db_course = db.get(Course, course_id)
    db_course.title = course_data.title
    db_course.description = course_data.description
    db_course.duration_hours = course_data.duration_hours
    db_course.price = course_data.price
    db.commit()
    db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int) -> bool:
    course = db.get(Course, course_id)
    if course:
        db.delete(course)
        db.commit()
        return True
    return False

def create_enrollment(db: Session, enrollment: EnrollmentCreate) -> Enrollment:
    student = db.get(Student, enrollment.student_id)
    course = db.get(Course, enrollment.course_id)

    if not student:
        raise ValueError("Student not found")
    if not course:
        raise ValueError("Course not found")

    existing = db.execute(
        select(Enrollment).where(
            (Enrollment.student_id == enrollment.student_id) &
            (Enrollment.course_id == enrollment.course_id)
        )
    ).scalar_one_or_none()

    if existing:
        raise ValueError("Enrollment already exists")

    db_enrollment = Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

def get_enrollment(db: Session, enrollment_id: int) -> Enrollment | None:
    return db.get(Enrollment, enrollment_id)

def get_all_enrollments(db: Session) -> list[Enrollment]:
    result = db.execute(select(Enrollment))
    return result.scalars().all()

def get_detailed_enrollments(db: Session) -> list[dict]:
    enrollments = get_all_enrollments(db)
    detailed = []

    for enrollment in enrollments:
        detailed.append({
            "enrollment": enrollment,
            "student": enrollment.student,
            "course": enrollment.course,
        })
    return detailed

def update_enrollment(db: Session, enrollment_id: int, enrollment_data: EnrollmentCreate) -> Enrollment:
    db_enrollment = db.get(Enrollment, enrollment_id)
    db_enrollment.student_id = enrollment_data.student_id
    db_enrollment.course_id = enrollment_data.course_id
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment


def delete_enrollment(db: Session, enrollment_id: int) -> bool:
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment:
        db.delete(enrollment)
        db.commit()
        return True
    return False

print("ORM crud operations created successfully")