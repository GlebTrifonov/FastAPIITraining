from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# TODO: Добавьте валидацию с Field (min_length, max_length, ge, le)
# Нет проверок на длину строк, диапазон возраста, формат email
# См. REVIEW.md секция "Критические проблемы" пункт 4
class Student(BaseModel):

    model_config = ConfigDict(from_attributes=True)


    id: int
    first_name: str  # TODO: Field(min_length=2, max_length=50)
    last_name: str  # TODO: Field(min_length=2, max_length=50)
    age: int  # TODO: Field(ge=16, le=100)
    email: Optional[str] = None  # TODO: EmailStr для валидации формата
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