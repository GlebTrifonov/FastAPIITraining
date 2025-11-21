from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class Student(BaseModel):

    model_config = ConfigDict(from_attributes=True)


    id: int
    first_name: str
    last_name: str
    age: int
    email: Optional[str] = None
    is_active: bool = True

class Course(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    id: int
    title: str
    description: Optional[str] = None
    duration_hours: float
    price: float = 0.0
    tags: List[str] = []


class Enrollment(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    id: int
    course_id: int
    student_id: int


class StudentCreate(BaseModel):
    """Модель для создания нового студента (без ID)"""
    first_name: str
    last_name: str
    age: int
    email: Optional[str] = None
    is_active: bool = True

class CourseCreate(BaseModel):
    """Модель для создания нового курса (без ID)"""
    title: str
    description: Optional[str] = None
    duration_hours: float
    price: float = 0.0

class EnrollmentCreate(BaseModel):
    """Модель для записи студента на курс (без ID)"""
    student_id: int
    course_id: int


print("Модели для API созданы успешно!")