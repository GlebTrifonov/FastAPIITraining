# 📋 Code Review: Student Management System

**Оценка:** 7/10 ⭐

Учебный проект системы управления студентами и курсами на FastAPI с SQLite. Код демонстрирует базовое понимание FastAPI, SQLAlchemy Core и CRUD операций. Хорошая структура с роутерами и тестами.

---

## ✅ Сильные стороны

### 1. **Чистая архитектура** 📁
- Разделение на роутеры (`students.py`, `courses.py`, `enrollments.py`)
- Отдельный модуль CRUD операций
- Pydantic модели для валидации
- HTML templates для фронтенда

### 2. **REST API дизайн** 🌐
```python
# Правильное использование HTTP методов
GET    /api/students/      - получить всех
GET    /api/students/{id}  - получить одного
POST   /api/students/      - создать
DELETE /api/students/{id}  - удалить
```

### 3. **Тестирование** ✅
```python
# tests/test_main.py - хорошее покрытие
class TestStudentsAPI:
    def test_create_student_success(self):
        ...
    def test_get_student_by_id_not_found(self):
        ...
```

### 4. **Health Check эндпоинт** ❤️
```python
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

### 5. **Docker Support** 🐳
- Dockerfile и docker-compose.yml присутствуют
- Volumes для персистентности данных

### 6. **Валидация бизнес-логики** ✨
```python
# crud.py - проверка дубликатов
if existing:
    raise ValueError("Студент уже записан на этот курс")
```

---

## 🔴 Критические проблемы

### 1. **КРИТИЧНО! Неправильный Foreign Key в enrollments** 🚨
**Файл:** `database.py:50-51`

```python
# ❌ ОШИБКА: student_id ссылается на courses.id вместо students.id
enrollments = Table(
    "enrollments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("student_id", Integer, ForeignKey("courses.id"), nullable=False),  # ❌ НЕПРАВИЛЬНО!
    Column("course_id", Integer, ForeignKey("courses.id"), nullable=False),
)
```

**Проблема:** `student_id` должен ссылаться на `students.id`, а не на `courses.id`!

**Решение:**
```python
# ✅ ПРАВИЛЬНО
enrollments = Table(
    "enrollments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("student_id", Integer, ForeignKey("students.id"), nullable=False),  # ✅
    Column("course_id", Integer, ForeignKey("courses.id"), nullable=False),
)
```

**Важность:** 🔥🔥🔥 **КРИТИЧНО** - нарушена целостность данных, enrollments работают некорректно!

---

### 2. **Использование SQLAlchemy Core вместо ORM** ⚠️
**Файл:** `database.py`

```python
# ❌ ПЛОХО: Table objects + manual SQL
students = Table("students", metadata, Column(...), ...)

# В crud.py - ручное построение словарей
student_dict = {
    "id": student_data[0],
    "first_name": student_data[1],
    ...
}
```

**Проблема:**
- Индексный доступ (`row[0]`, `row[1]`) подвержен ошибкам
- Нет типобезопасности
- Больше кода для CRUD операций
- Нет автоматического маппинга

**Решение:** Использовать SQLAlchemy ORM
```python
# ✅ ЛУЧШЕ: Декларативные модели
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int]
    email: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")

# CRUD становится проще
def create_student(session: Session, student: StudentCreate) -> Student:
    db_student = Student(**student.dict())
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student

def get_student(session: Session, student_id: int) -> Student | None:
    return session.get(Student, student_id)
```

---

### 3. **metadata.create_all() вместо миграций** 🔄
**Файл:** `database.py:58`

```python
# ❌ ПРОБЛЕМА
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)  # Создает таблицы при импорте модуля
```

**Почему плохо:**
- При изменении схемы данные теряются
- Нет версионирования БД
- Невозможен откат изменений

**Решение:** Alembic миграции
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

---

### 4. **Нет валидации в Pydantic моделях** 📝
**Файл:** `models.py`

```python
# ❌ ПРОБЛЕМА: нет ограничений
class StudentCreate(BaseModel):
    first_name: str  # может быть пустой или 1000 символов
    last_name: str
    age: int  # может быть отрицательным или 999
    email: Optional[str] = None  # нет проверки формата email
```

**Решение:**
```python
from pydantic import BaseModel, Field, EmailStr, field_validator

class StudentCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, pattern="^[A-Za-zА-Яа-я]+$")
    last_name: str = Field(..., min_length=2, max_length=50, pattern="^[A-Za-zА-Яа-я]+$")
    age: int = Field(..., ge=16, le=100, description="Возраст от 16 до 100 лет")
    email: EmailStr | None = None  # автоматическая валидация email
    is_active: bool = True
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 16:
            raise ValueError('Студент должен быть старше 16 лет')
        return v

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    duration_hours: float = Field(..., gt=0, le=1000)
    price: float = Field(default=0.0, ge=0)
```

---

### 5. **Отсутствие обработки ошибок БД** 💥
**Файл:** `crud.py`

```python
# ❌ ПРОБЛЕМА: нет try/except
def create_student(student: StudentCreate) -> Student:
    with get_connection() as conn:
        query = insert(students).values(...)
        result = conn.execute(query)  # может упасть
        conn.commit()  # может упасть при constraint violation
```

**Решение:**
```python
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

def create_student(student: StudentCreate) -> Student:
    try:
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
            
    except IntegrityError as e:
        # Нарушение unique constraint
        if "email" in str(e.orig):
            raise ValueError(f"Email {student.email} уже используется")
        raise ValueError("Ошибка создания студента")
    except SQLAlchemyError as e:
        raise RuntimeError(f"Ошибка базы данных: {str(e)}")
```

---

### 6. **Неиспользуемый databases library** 🤔
**Файл:** `database.py:8`

```python
import databases

database = databases.Database(DATABASE_URL)  # создан, но нигде не используется
```

**Проблема:** 
- Импортируется `databases` для async работы, но не используется
- Все CRUD операции синхронные через `engine.connect()`

**Решение:** Либо убрать `databases`, либо переписать CRUD на async:
```python
# Вариант 1: Убрать (если не нужен async)
# import databases  # удалить
# database = databases.Database(...)  # удалить

# Вариант 2: Использовать async (более продвинуто)
from databases import Database

database = Database(DATABASE_URL)

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Async CRUD
async def get_all_students() -> list[Student]:
    query = select(students)
    rows = await database.fetch_all(query)
    return [Student(**dict(row)) for row in rows]
```

---

### 7. **Отсутствие logging** 📝
**Файл:** `crud.py:233`

```python
print("CRUD is created")  # ❌ print вместо logging
```

**Решение:**
```python
import logging

logger = logging.getLogger(__name__)

# В main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# В crud.py
logger.info("Student created", extra={"student_id": new_id})
logger.error(f"Failed to create student: {e}", exc_info=True)
```

---

## 💡 Рекомендации

### 1. **Добавить поле tags в Course** 🏷️
**Файл:** `models.py:24`

```python
# ❌ В Pydantic есть, в БД нет
class Course(BaseModel):
    tags: List[str] = []  # это поле нигде не сохраняется!
```

**Решение:**
```python
# database.py
courses = Table(
    "courses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(100), nullable=False),
    Column("description", String(500), nullable=True),
    Column("duration_hours", Float, nullable=False),
    Column("price", Float, default=0.0),
    Column("tags", String(200)),  # ✅ добавить как JSON или comma-separated
)

# crud.py
def create_course(course: CourseCreate) -> Course:
    query = insert(courses).values(
        title=course.title,
        description=course.description,
        duration_hours=course.duration_hours,
        price=course.price,
        tags=",".join(course.tags) if course.tags else ""  # ✅ сохраняем
    )
```

---

### 2. **Добавить PUT endpoint для обновления** ✏️
Сейчас есть только POST, GET, DELETE. Добавьте UPDATE:

```python
# routers/students.py
@router.put("/{student_id}", response_model=Student)
async def update_student(student_id: int, student: StudentCreate):
    updated = crud.update_student(student_id, student)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated

# crud.py
def update_student(student_id: int, student_data: StudentCreate) -> Student | None:
    with get_connection() as conn:
        query = update(students).where(students.c.id == student_id).values(
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            age=student_data.age,
            email=student_data.email,
            is_active=student_data.is_active
        )
        result = conn.execute(query)
        conn.commit()
        
        if result.rowcount > 0:
            return get_student(student_id)
        return None
```

---

### 3. **Добавить CORS middleware** 🌐
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 4. **Улучшить тесты** 🧪
```python
# tests/test_main.py - добавить тесты
class TestEnrollmentsAPI:
    def test_enroll_student_twice_should_fail(self):
        """Тест на предотвращение дублирования записи"""
        student = client.post("/api/students/", json={...}).json()
        course = client.post("/api/courses/", json={...}).json()
        
        # Первая запись - ОК
        response1 = client.post("/api/enroll/", json={
            "student_id": student["id"],
            "course_id": course["id"]
        })
        assert response1.status_code == 200
        
        # Вторая запись - должна быть ошибка
        response2 = client.post("/api/enroll/", json={
            "student_id": student["id"],
            "course_id": course["id"]
        })
        assert response2.status_code == 400
        assert "уже записан" in response2.json()["detail"]
    
    def test_enroll_nonexistent_student(self):
        """Тест записи несуществующего студента"""
        course = client.post("/api/courses/", json={...}).json()
        
        response = client.post("/api/enroll/", json={
            "student_id": 999,  # не существует
            "course_id": course["id"]
        })
        assert response.status_code == 400
```

---

### 5. **Добавить пагинацию** 📄
```python
# routers/students.py
from fastapi import Query

@router.get("/", response_model=list[Student])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    students = crud.get_all_students(skip=skip, limit=limit)
    return students

# crud.py
def get_all_students(skip: int = 0, limit: int = 100) -> list[Student]:
    with get_connection() as conn:
        query = select(students).offset(skip).limit(limit)
        result = conn.execute(query)
        # ...
```

---

### 6. **Улучшить Docker setup** 🐳
```yaml
# docker-compose.yml
version: '3.8'

services:
  fastapi-app:
    build: .
    ports:
      - "8000:8000"
    container_name: fastapi-courses-app
    restart: unless-stopped
    
    environment:
      - DATABASE_URL=sqlite:///./data/student_management.db
      - PYTHONPATH=/app
      - LOG_LEVEL=INFO  # ✅ добавить
    
    volumes:
      - ./data:/app/data
      - ./FirstAPIProject:/app  # ✅ для hot reload
    
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload  # ✅ явная команда
    
    healthcheck:  # ✅ добавить health check
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

### 7. **Добавить фильтрацию и поиск** 🔍
```python
# routers/students.py
@router.get("/search/", response_model=list[Student])
async def search_students(
    query: str = Query(..., min_length=2),
    is_active: bool | None = None
):
    students = crud.search_students(query, is_active)
    return students

# crud.py
def search_students(search_query: str, is_active: bool | None = None) -> list[Student]:
    with get_connection() as conn:
        query = select(students).where(
            (students.c.first_name.ilike(f"%{search_query}%")) |
            (students.c.last_name.ilike(f"%{search_query}%"))
        )
        
        if is_active is not None:
            query = query.where(students.c.is_active == is_active)
        
        result = conn.execute(query)
        # ...
```

---

## 📊 Оценка по критериям

| Критерий | Оценка | Комментарий |
|----------|---------|-------------|
| **Архитектура** | 7/10 | Хорошее разделение на роутеры, но SQLAlchemy Core |
| **Безопасность** | 5/10 | Нет валидации, неправильный FK |
| **База данных** | 6/10 | SQLAlchemy Core вместо ORM, нет миграций |
| **Обработка ошибок** | 5/10 | Минимальная, нет try/except в CRUD |
| **Валидация** | 5/10 | Базовая Pydantic, нет Field ограничений |
| **Тестирование** | 8/10 | Хорошие тесты, но мало edge cases |
| **Документация** | 6/10 | Есть README, но пустой в корне |
| **Docker** | 7/10 | Есть, но можно улучшить |
| **Код-стайл** | 7/10 | Чистый код, но print вместо logging |
| **Функциональность** | 7/10 | CRUD есть, но нет UPDATE endpoints |

**Общая оценка:** 7.0/10 ⭐

---

## 🎯 План исправлений

### Критические (1 день):
1. ✅ **Исправить Foreign Key** в enrollments (student_id → students.id)
2. ✅ Добавить валидацию Pydantic (Field, min_length, max_length, ge, le)
3. ✅ Добавить обработку ошибок БД (try/except IntegrityError)
4. ✅ Сохранять поле tags в базу данных

### Важные (2-3 дня):
5. ✅ Добавить PUT endpoints для обновления
6. ✅ Настроить Alembic миграции
7. ✅ Заменить print на logging
8. ✅ Добавить CORS middleware

### Желательные (неделя):
9. ⚡ Переписать на SQLAlchemy ORM (вместо Core)
10. ⚡ Добавить пагинацию и фильтрацию
11. ⚡ Расширить тесты (edge cases, enrollments)
12. ⚡ Улучшить Docker setup с health checks

---

## 💬 Заключение

**Хороший учебный проект!** 👏 Код демонстрирует:
- ✅ Понимание FastAPI и REST API
- ✅ Работа с SQLAlchemy
- ✅ Структурирование приложения
- ✅ Написание тестов

**Основные проблемы:**
1. 🔥 Критическая ошибка в Foreign Key (enrollments)
2. ⚠️ Использование SQLAlchemy Core вместо ORM
3. ⚠️ Нет валидации и обработки ошибок
4. ⚠️ metadata.create_all() вместо миграций

**Что делать дальше:**
1. Исправить FK в enrollments
2. Добавить валидацию Pydantic
3. Переписать на SQLAlchemy ORM
4. Настроить Alembic
5. Добавить UPDATE endpoints

После исправления критических замечаний проект будет отличным примером для портфолио! 🚀

**Рекомендуемая оценка после исправлений:** 8.5/10
