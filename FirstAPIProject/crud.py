from unittest import result

from sqlalchemy import create_engine, select, insert, update, delete
from database import students, courses, enrollments, engine
from models import Student, StudentCreate, Course, CourseCreate, Enrollment, EnrollmentCreate
from routers.enrollments import get_enrollments


def get_connection():
    return engine.connect()

#CRUD for students
def create_student(student: StudentCreate) -> Student:
    with get_connection() as conn:
        query = insert(students).values(
            first_name=student.first_name,
            last_name=student.last_name,
            age=student.age,
            email=student.email,
            is_active=student.is_active
        )

        result = conn.execute(query)
        conn.commit()

        new_id = result.inserted_primary_key[0]
        return get_student(new_id)


def get_student(student_id: int) -> Student:
    """Получить студента по ID"""
    with get_connection() as conn:
        query = select(students).where(students.c.id == student_id)
        result = conn.execute(query)
        student_data = result.fetchone()

        if student_data:
            student_dict = {
                "id": student_data[0],
                "first_name": student_data[1],
                "last_name": student_data[2],
                "age": student_data[3],
                "email": student_data[4],
                "is_active": student_data[5]
            }
            return Student(**student_dict)
        return None

def get_all_students() -> list[Student]:
    with get_connection() as conn:
        query = select(students)
        result = conn.execute(query)

        students_list = []
        for row in result:
            student_dict = {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "age": row[3],
                "email": row[4],
                "is_active": row[5]
            }
            students_list.append(Student(**student_dict))

        return students_list


def delete_student(student_id: int) -> bool:
    """Удалить студента по ID"""
    with get_connection() as conn:
        query = delete(students).where(students.c.id == student_id)
        result = conn.execute(query)
        conn.commit()

        return result.rowcount > 0

#CRUD for course
def create_course(course: CourseCreate) -> Course:
    """Создать новый курс"""
    with get_connection() as conn:
        query = insert(courses).values(
            title=course.title,
            description=course.description,
            duration_hours=course.duration_hours,
            price=course.price
        )

        result = conn.execute(query)
        conn.commit()

        new_id = result.inserted_primary_key[0]
        return get_course(new_id)


def get_course(course_id: int) -> Course:
    """Получить курс по ID"""
    with get_connection() as conn:
        query = select(courses).where(courses.c.id == course_id)
        result = conn.execute(query)
        course_data = result.fetchone()

        if course_data:
            course_dict = {
                "id": course_data[0],
                "title": course_data[1],
                "description": course_data[2],
                "duration_hours": course_data[3],
                "price": course_data[4]
            }
            return Course(**course_dict)
        return None


def get_all_courses() -> list[Course]:
    """Получить все курсы"""
    with get_connection() as conn:
        query = select(courses)
        result = conn.execute(query)

        courses_list = []
        for row in result:
            course_dict = {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "duration_hours": row[3],
                "price": row[4]
            }
            courses_list.append(Course(**course_dict))

        return courses_list


def delete_course(course_id: int) -> bool:
    """Удалить курс по ID"""
    with get_connection() as conn:
        query = delete(courses).where(courses.c.id == course_id)
        result = conn.execute(query)
        conn.commit()

        return result.rowcount > 0


def create_enrollment(enrollment: EnrollmentCreate) -> Enrollment:
    with get_connection() as conn:
        student = get_student(enrollment.student_id)
        if not student:
            raise ValueError(f"Студент с ID {enrollment.student_id} не найден")

        course = get_course(enrollment.course_id)
        if not course:
            raise ValueError(f"Курс с ID {enrollment.course_id} не найден")

        existing = conn.execute(
            select(enrollments).where(
                (enrollments.c.student_id == enrollment.student_id) &
                (enrollments.c.course_id == enrollment.course_id)
            )
        ).fetchone()

        if existing:
            raise ValueError("Студент уже записан на этот курс")

        query = insert(enrollments).values(
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
        )

        result = conn.execute(query)
        conn.commit()

        new_id = result.inserted_primary_key[0]
        return get_enrollment(new_id)

def get_enrollment(enrollment_id: int) -> Enrollment:
    with get_connection() as conn:
        query = select(enrollments).where(enrollments.c.id == enrollment_id)
        result = conn.execute(query)
        enrollment_data = result.fetchone()

        if enrollment_data:
            enrollment_dict = {
                "id": enrollment_data[0],
                "student_id": enrollment_data[1],
                "course_id": enrollment_data[2],
            }
            return Enrollment(**enrollment_dict)
        return None

def get_all_enrollments() -> list[Enrollment]:
    with get_connection() as conn:
        query = select(enrollments)
        result = conn.execute(query)

        enrollments_list = []
        for row in result:
            enrollment_dict = {
                "id": row[0],
                "student_id": row[1],
                "course_id": row[2],
            }
            enrollments_list.append(Enrollment(**enrollment_dict))

        return enrollments_list

def get_detailed_enrollments() -> list[dict]:
    enrollments = get_all_enrollments()
    detailed = []

    for enrollment in enrollments:
        student = get_student(enrollment.student_id)
        course = get_course(enrollment.course_id)

        if student and course:
            detailed.append({
                "enrollment": enrollment,
                "student": student,
                "course": course
            })
    return detailed


def delete_enrollment(enrollment_id: int) -> bool:
    with get_connection() as conn:
        query = delete(enrollments).where(enrollments.c.id == enrollment_id)
        result = conn.execute(query)
        conn.commit()

        return result.rowcount > 0


print("CRUD is created")