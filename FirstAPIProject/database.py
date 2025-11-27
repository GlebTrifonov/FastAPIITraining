from sqlalchemy import create_engine, String, Integer, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "student"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int]
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", back_populates="student"
    )


class Course(Base):
    __tablename__ = "course"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_hours: Mapped[float]
    price: Mapped[float] = mapped_column(default=0.0)

    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", back_populates="course"
    )


class Enrollment(Base):
    __tablename__ = "enrollment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"))

    student: Mapped["Student"] = relationship("Student", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")


engine = create_engine("sqlite:///student_management.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


print("ORM models created successfully")
