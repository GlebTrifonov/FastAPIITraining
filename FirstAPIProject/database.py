import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
import databases

DATABASE_URL = "sqlite:///./student_management.db"

# TODO: Неиспользуемый import - databases нигде не применяется
# Либо уберите, либо переп ишите CRUD на async
# См. REVIEW.md секция "Критические проблемы" пункт 6
database = databases.Database(DATABASE_URL) #асинхронное подкл к БД
metadata = MetaData() #Инфо о структуре таблиц
Base = declarative_base()

# Students
students = Table(
     "students",
     metadata,

     Column("id", Integer, primary_key=True),

     Column("first_name", String(50), nullable=False),

     Column("last_name", String(50), nullable=False),

     Column("age", Integer, nullable=False),

     Column("email", String(100), nullable=True),

     Column("is_active", Boolean, default=True),
 )

courses = Table(
    "courses",
    metadata,

    Column("id", Integer, primary_key=True),

    Column("title", String(100), nullable=False),

    Column("description", String(500), nullable=True),

    Column("duration_hours", Float, nullable=False),

    Column("price", Float, default=0.0),
 )

enrollments = Table(
    "enrollments",
    metadata,

    Column("id", Integer, primary_key=True),

    # TODO: КРИТИЧНО! Неправильный Foreign Key - student_id должен ссылаться на students.id, а не courses.id
    # Сейчас: ForeignKey("courses.id") ❌
    # Должно быть: ForeignKey("students.id") ✅
    # См. REVIEW.md секция "Критические проблемы" пункт 1
    Column("student_id", Integer, ForeignKey("courses.id"), nullable=False),

    Column("course_id", Integer, ForeignKey("courses.id"), nullable=False),
)


engine = create_engine(DATABASE_URL)
# TODO: Удалите metadata.create_all() и используйте Alembic миграции
# При изменении схемы БД все данные ТЕРЯЮТСЯ!
# См. REVIEW.md секция "Критические проблемы" пункт 3
metadata.create_all(engine)



print("________DB is created________")