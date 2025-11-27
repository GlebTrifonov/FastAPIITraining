from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import uvicorn

# Импортируем роутеры
from routers.students import router as students_router
from routers.courses import router as courses_router
from routers.enrollments import router as enrollments_router
from database import create_tables

create_tables()

# 1. СОЗДАНИЕ ПРИЛОЖЕНИЯ
app = FastAPI(
    title="Мой учебный API",
    version="1.0.0",
    description="Этот API создан для изучения FastAPI",
)

# 2. ПОДКЛЮЧАЕМ РОУТЕРЫ
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(enrollments_router)



# 3. HTML СТРАНИЦЫ
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>HTML file not found</h1>")


@app.get("/students/", response_class=HTMLResponse)
async def students_page():
    from routers.students import students_page as students_handler

    return await students_handler()


@app.get("/courses/", response_class=HTMLResponse)
async def courses_page():
    from routers.courses import courses_page as courses_handler

    return await courses_handler()


@app.get("/enrollments/", response_class=HTMLResponse)
async def enrollments_page():
    from routers.enrollments import enrollments_page as enrollments_handler

    return await enrollments_handler()


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Student Management System работает корректно",
        "version": "2.0.0",
        "database": "SQLite",
    }


# 4. БАЗОВЫЙ ЭНДПОИНТ
@app.get("/api/")
async def root():
    return {"message": "It's Student Management System"}


if __name__ == "__main__":
    print(" Запускаем сервер на http://localhost:8000")
    print(" Документация API: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
