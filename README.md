# Students & Courses API

Система управления студентами и курсами: REST API на FastAPI и SQLAlchemy ORM.

## Особенности

- REST API: студенты, курсы, записи на курсы
- SQLAlchemy ORM
- Автоматическая документация Swagger/OpenAPI
- Валидация с Pydantic
- Unit и интеграционные тесты с pytest
- Docker и Docker Compose
- Миграции схемы через Alembic

## Технологический стек

- FastAPI, Python 3.8+
- SQLite / MySQL, SQLAlchemy ORM
- Alembic
- pytest
- Docker, Docker Compose

## Запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/GlebTrifonov/FastAPIITraining.git
   cd FastAPIITraining/FirstAPIProject
   ```
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Запустите приложение:
   ```bash
   uvicorn main:app --reload
   ```
5. Откройте в браузере:
   - документация API: http://localhost:8000/docs
   - веб-интерфейс: http://localhost:8000

## Тесты

```bash
pytest
```

## Миграции БД (Alembic)

```bash
alembic revision --autogenerate -m "Initial tables"  # создать миграцию
alembic upgrade head                                 # применить
alembic downgrade -1                                 # откатить последнюю
```
