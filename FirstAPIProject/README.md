https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
https://img.shields.io/badge/SQLAlchemy-1.4.29-red?style=for-the-badge
https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white

Полнофункциональная система управления студентами и курсами с современным REST API, построенная на FastAPI и SQLAlchemy ORM.


Особенности:
- Современный REST API
- SQLAlchemy ORM
- Автоматическая генерация Swagger/OpenAPI документации
- Строгая валидация с Pydantic
- Unit и интеграционные тесты с pytest
- Docker поддержка
- Управление схемой миграций через Alembic



Технологический стек:
- FastAPI, Python 3.8+
- SQLite / MySQL с SQLAlchemy ORM
- Alembic
- Pytest
- Docker, Docker Compose


Старт проекта:
1. Клонируйте репозиторий:
git clone <your-repo-url>
cd FirstAPIProject
2. Создайте виртуальное окружение:
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
3. Установите зависимости:
pip install -r requirements.txt
4. Запустите приложение:
uvicorn main:app --reload
5. Откройте в браузере:
API Documentation: http://localhost:8000/docs
Web Interface:     http://localhost:8000


Запуск тестов:
pytest

Миграции БД:
Настройка Alembic
# Инициализация
alembic init alembic

# Создание миграции
alembic revision --autogenerate -m "Initial tables"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1