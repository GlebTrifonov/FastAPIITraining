from pydantic import BaseModel, ConfigDict, field_validator, EmailStr, Field
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

    first_name: str = Field(min_length=2, max_length=50, pattern=r"^[A-Za-zА-Яа-я]+$")
    last_name: str = Field(min_length=2, max_length=50, pattern=r"^[A-Za-zА-Яа-я]+$")
    age: int = Field(ge=16, le=100, description="Возраст от 16 до 100 лет")
    email: EmailStr | None = None
    is_active: bool = True

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 16:
            raise ValueError("Студент должен быть старше 16 лет")
        return v


class CourseCreate(BaseModel):
    """Модель для создания нового курса (без ID)"""

    title: str = Field(min_length=2, max_length=50)
    description: str | None = Field(None, max_length=500)
    duration_hours: float = Field(gt=0, le=1000)
    price: float = Field(default=0.0, ge=0)


class EnrollmentCreate(BaseModel):
    """Модель для записи студента на курс (без ID)"""

    student_id: int
    course_id: int


print("Модели для API созданы успешно!")
