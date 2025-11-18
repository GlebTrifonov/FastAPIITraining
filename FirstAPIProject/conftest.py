import pytest
import sys
import os


# Добавляем путь к проекту в PythonPath
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def test_client():
    """Фикстура для тестового клиента"""
    from main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    return client
