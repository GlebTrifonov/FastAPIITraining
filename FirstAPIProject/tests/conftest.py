import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Добавляем путь к родительской директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from main import app
from database import Base, get_db


@pytest.fixture(scope="function")
def test_client():
    """Фикстура для тестового клиента - пересоздает БД для каждого теста"""
    TEST_DATABASE_URL = "sqlite:///:memory:"

    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 🔧 ВАЖНО: Сначала создаем все таблицы
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Переопределяем зависимость БД
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()
