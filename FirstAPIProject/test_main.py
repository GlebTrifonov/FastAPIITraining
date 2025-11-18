import pytest
from fastapi.testclient import TestClient
from main import app, students_db, courses_db, enrollments_db

# Create test client
client = TestClient(app)


# Очистка БД перед тестами
@pytest.fixture(autouse=True)
def clean_databases():
    students_db.clear()
    courses_db.clear()
    enrollments_db.clear()
    yield


class TestStudentsAPI:
    """Тестим эндпоинтов для студентов"""

    def test_get_empty_students(self):
        """Тест получения пустого списка студентов"""
        response = client.get("/api/students/")
        assert response.status_code == 200
        assert response.json() == {"students": []}

    """Тест успешного создания студента"""

    def test_create_student_success(self):
        student_data = {
            "id": 1,
            "first_name": "Ivan",
            "last_name": "Smith",
            "age": 20,
            "email": "ivan@test.py",
            "is_active": True,
        }

        response = client.post("/api/students/", json=student_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Студент создан"
        assert data["student"]["id"] == 1
        assert data["student"]["first_name"] == "Ivan"

    def test_create_student_duplicate_id(self):
        """ "Студенты с дублирующимся ID"""
        student_data = {
            "id": 1,
            "first_name": "Иван",
            "last_name": "Петров",
            "age": 20,
            "email": "ivan@test.ru",
            "is_active": True,
        }
        client.post("/api/students/", json=student_data)

        # Create student with the same ID
        response = client.post("/api/students/", json=student_data)
        assert response.status_code == 400
        assert "Student With This ID Already Exist" in response.json()["detail"]

    def test_create_student_validation_error(self):
        invalid_data = {
            "id": 1,
            # No first_name and last_name
            "age": 20,
        }

        response = client.post("/api/students/", json=invalid_data)
        assert response.status_code == 422  # Unprocessable Entity

    def test_get_student_by_id_success(self):
        """ПОлучение студента по ID"""
        student_data = {
            "id": 1,
            "first_name": "Ivan",
            "last_name": "Smith",
            "age": 20,
            "email": "ivan@test.py",
            "is_active": True,
        }
        client.post("/api/students/", json=student_data)

        # ПОлучаем студента по ID
        response = client.get("/api/students/1")
        assert response.status_code == 200
        data = response.json()
        assert data["student"]["id"] == 1
        assert data["student"]["first_name"] == "Ivan"

    def test_get_student_by_id_not_found(self):
        """Тест получания несуществующего студента"""
        response = client.get("/api/students/999")
        assert response.status_code == 404
        assert "Not Found" in response.json()["detail"]


class TestCoursesAPI:
    """Тесты для курсов"""

    def test_get_empty_courses(self):
        """Тест получения пустого списка"""
        response = client.get("/api/courses/")
        assert response.status_code == 200
        assert response.json() == {"courses": []}

    def test_create_course_success(self):
        """Успешное создание курса"""
        course_data = {
            "id": 1,
            "title": "Математика",
            "description": "Высшая математика",
            "duration_hours": 64,
            "price": 5000.0,
        }

        response = client.post("/api/courses/", json=course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Course created successfully"
        assert data["course"]["title"] == "Математика"
        assert data["course"]["price"] == 5000.0

    def test_create_course_without_description(self):
        course_data = {
            "id": 1,
            "title": "Программирование",
            "duration_hours": 80,
            "price": 7000.0,
            # Без description
        }

        response = client.post("/api/courses/", json=course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["course"]["description"] is None


class TestEnrollmentsAPI:
    """Тест записей на курсы"""

    def setUp(
        self,
    ):  # setUp- метод из unittest, который вызывается перед КАЖДЫМ тестом!!!
        """создание студентов и курсы"""
        self.students_data = {
            "id": 1,
            "first_name": "Иван",
            "last_name": "Петров",
            "age": 20,
            "email": "ivan@test.ru",
            "is_active": True,
        }

        self.course_data = {
            "id": 1,
            "title": "Математика",
            "description": "Высшая математика",
            "duration_hours": 64,
            "price": 5000.0,
        }

        client.post("/api/students/", json=self.students_data)
        client.post("/api/courses/", json=self.course_data)

    def test_get_empty_enrollments(self):
        """Получение пустого списка записей"""
        response = client.get("/api/enrollments/")
        assert response.status_code == 200
        assert response.json() == {"enrollments": []}

    def test_enrollment_student_success(self):
        """Успешная запись на курс"""
        self.setUp()

        enrollment_data = {
            "id": 1,
            "student_id": 1,
            "course_id": 1,
        }

        response = client.post("/api/enroll/", json=enrollment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Student Enrolled Successfully"
        assert data["enrollment"]["id"] == 1
        assert data["enrollment"]["student_id"] == 1
        assert data["enrollment"]["course_id"] == 1

    def test_enroll_student_not_found(self):
        """Несуществующий студент"""
        self.setUp()

        enrollment_data = {
            "id": 1,
            "student_id": 999,  # Not found
            "course_id": 1,
        }

        response = client.post("/api/enroll/", json=enrollment_data)
        assert response.status_code == 404
        assert "Student Not Found" in response.json()["detail"]

    def test_enroll_course_not_found(self):
        """Несуществющий курс"""
        self.setUp()

        enrollment_data = {
            "id": 1,
            "student_id": 1,
            "course_id": 999,
        }

        response = client.post("/api/enroll/", json=enrollment_data)
        assert response.status_code == 404
        assert "Course Not Found" in response.json()["detail"]

    def test_enroll_duplicate(self):
        """Дублирующая запись"""
        self.setUp()

        enrollment_data = {"id": 1, "student_id": 1, "course_id": 1}

        client.post("/api/enroll/", json=enrollment_data)  # Первая запись

        # Вторая такая же должна вернуть ошибку
        response = client.post("/api/enroll/", json=enrollment_data)
        assert response.status_code == 400
        assert "Студент записан на этот курс" in response.json()["detail"]


class TestHTMLPages:
    """Тесты для HTML страниц"""

    def test_main_page(self):
        """Главная страница"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_student_page(self):
        """Страница студентов"""
        response = client.get("/students")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_course_page(self):
        """Страница курсов"""
        response = client.get("/courses")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestErrorCases:
    """Тест ощибок"""

    def test_invalid_json(self):
        """Тест отправки невалидного JSON"""
        response = client.post(
            "/api/students/", data="invalid json"
        )  # IDE не понимает, что вы намеренно отправляете некорректные данные для тестирования
        assert response.status_code == 422

    def test_wrong_http_method(self):
        """Тест использования неправильного HTTP метода"""
        response = client.put("/api/students/")  # PUT instead of POST
        assert response.status_code == 405  # Method Not Allowed

    def test_nonexistent_endpoint(self):
        """Тест обращения к несуществующему эндпоинту"""
        response = client.get("/api/nonexistent/")
        assert response.status_code == 404


if __name__ == "__main__":
    # Запуск тестов напрямую (альтернатива pytest)
    pytest.main([__file__, "-v"])
