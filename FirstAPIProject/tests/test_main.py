import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from database import engine, students, courses, enrollments
from sqlalchemy import delete

# Create test client
client = TestClient(app)


# Очистка БД перед тестами
@pytest.fixture(autouse=True)
def clean_databases():
    with engine.connect() as conn:
        conn.execute(delete(enrollments))
        conn.execute(delete(students))
        conn.execute(delete(courses))
        conn.commit()
    yield
    print("Тест завершен, База очищена!")

class TestStudentsAPI:
    """Тестим эндпоинтов для студентов"""

    def test_get_empty_students(self):
        """Тест получения пустого списка студентов"""
        response = client.get("/api/students/")
        assert response.status_code == 200
        assert response.json() == []
        print("Отработали пустой список студентов")


    def test_create_student_success(self):
        """Тест успешного создания студента"""
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
        assert data["first_name"] == "Ivan"
        assert "id" in data
        print(f" Создан студент с ID: {data['id']}")


    def test_create_student_validation_error(self):
        invalid_data = {
            "age": 20,
        }
        response = client.post("/api/students/", json=invalid_data)
        assert response.status_code == 422
        print("Ошибка валидации обработана")


    def test_get_student_by_id_success(self):
        """ПОлучение студента по ID"""
        student_data = {
            "first_name": "Ivan",
            "last_name": "Smith",
            "age": 20,
            "email": "ivan@test.py",
            "is_active": True,
        }
        create_response = client.post("/api/students/", json=student_data)
        student_id = create_response.json()["id"]
        response = client.get(f"/api/students/{student_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == student_id
        assert data["first_name"] == "Ivan"
        print(f"Получен студент с ID: {student_id}")


    def test_get_student_by_id_not_found(self):
        """Тест получания несуществующего студента"""
        response = client.get("/api/students/999")
        assert response.status_code == 404
        assert "Student not found" in response.json()["detail"]
        print("Обработано отсутствие студента")


    def test_delete_student_success(self):
        """Удаление студента"""
        student_data = {
            "first_name": "Ivan",
            "last_name": "Smith",
            "age": 20,
        }
        create_response = client.post("/api/students/", json=student_data)
        student_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/students/{student_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Student deleted successfully"

        get_response = client.get(f"/api/students/{student_id}")
        assert get_response.status_code == 404
        print(f"Студент с ID: {student_id} успешно удален")


class TestCoursesAPI:
    """Тесты для курсов"""

    def test_get_empty_courses(self):
        """Тест получения пустого списка"""
        response = client.get("/api/courses/")
        assert response.status_code == 200
        assert response.json() == []
        print("Отработали пустой список курсов")

    def test_create_course_success(self):
        """Успешное создание курса"""
        course_data = {
            "title": "Математика",
            "description": "Высшая математика",
            "duration_hours": 64,
            "price": 5000.0,
        }

        response = client.post("/api/courses/", json=course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Математика"
        assert data["description"] == "Высшая математика"
        assert data["duration_hours"] == 64
        assert data["price"] == 5000.0
        assert "id" in data

        print(f"Создан ку ID: {data['id']}")

    def test_create_course_without_description(self):
        course_data = {
            "title": "Программирование",
            "duration_hours": 80,
            "price": 7000.0,
            # Без description
        }

        response = client.post("/api/courses/", json=course_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] is None
        assert data["title"] == "Программирование"

        print("Обработан курс без описания")

    def test_create_course_validation_error(self):
        invalid_data = {
            "description": "Курс без названия",
            "price": 1000.0,
        }

        response = client.post("/api/courses/", json=invalid_data)

        assert response.status_code == 422
        print("Обработана ошибка валидации курса")

    def test_get_course_by_id_success(self):
        course_data = {
            "title": "Test course",
            "duration_hours": 40,
            "price": 3000.0,
        }
        create_response = client.post("/api/courses/", json=course_data)
        course_id = create_response.json()["id"]

        response = client.get(f"/api/courses/{course_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test course"
        assert data["id"] == course_id

        print(f"Обработано получение курса по ID: {course_id}")

    def test_get_course_by_id_not_found(self):
        response = client.get("/api/courses/999")
        assert response.status_code == 404
        assert "Course not found" in response.json()["detail"]
        print("Отсутствие курса обработано")

    def test_delete_course_success(self):
        course_data = {
            "title": "Test course",
            "duration_hours": 40,
            "price": 3000.0,
        }
        create_response = client.post("/api/courses/", json=course_data)
        course_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/courses/{course_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Course deleted successfully"

        get_response = client.get(f"/api/courses/{course_id}")
        assert get_response.status_code == 404

        print(f"Курс с ID: {course_id} deleted")


class TestEnrollmentsAPI:
    """Тест записей на курсы"""
    def create_test_data(self):
        student_data = {
            "first_name": "Иван",
            "last_name": "Петров",
            "age": 20,
            "email": "ivan@test.ru",
        }
        student_response = client.post("/api/students/", json=student_data)
        student_id = student_response.json()["id"]

        course_data = {
            "title": "Математика",
            "description": "Высшая математика",
            "duration_hours": 64,
            "price": 5000.0,
        }
        course_response = client.post("/api/courses/", json=course_data)
        course_id = course_response.json()["id"]

        return student_id, course_id

    def test_get_empty_enrollments(self):
        """Получение пустого списка записей"""
        response = client.get("/api/enrollments/")
        assert response.status_code == 200
        assert response.json() == []

    def test_enrollment_student_success(self):
        """Успешная запись на курс"""
        student_id, course_id = self.create_test_data()

        enrollment_data = {
            "student_id": student_id,
            "course_id": course_id,
        }

        response = client.post("/api/enroll/", json=enrollment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == student_id
        assert data["course_id"] == course_id
        assert "id" in data

        print(f"Создана записть на курс с ID: {data['id']}")

    def test_enroll_student_not_found(self):
        """Несуществующий студент"""
        _, course_id = self.create_test_data()

        enrollment_data = {
            "student_id": 999,  # Not found
            "course_id": course_id,
        }

        response = client.post("/api/enroll/", json=enrollment_data)
        assert response.status_code == 400
        assert "Студент с ID 999 не найден" in response.json()["detail"]
        print("Обработана ошибка несуществующего студента")

    def test_enroll_course_not_found(self):
        """Несуществющий курс"""
        student_id, _ = self.create_test_data()

        enrollment_data = {
            "student_id": student_id,
            "course_id": 999,
        }

        response = client.post("/api/enroll/", json=enrollment_data)
        assert response.status_code == 400
        assert "Курс с ID 999 не найден" in response.json()["detail"]
        print("Ошибка несуществующего курса обработана")

    def test_enroll_duplicate(self):
        """Дублирующая запись"""
        student_id, course_id = self.create_test_data()

        enrollment_data = {
            "student_id": student_id,
            "course_id": course_id,
            }

        first_response = client.post("/api/enroll/", json=enrollment_data)  # Первая запись
        assert first_response.status_code == 200

        # Вторая такая же должна вернуть ошибку
        second_response = client.post("/api/enroll/", json=enrollment_data)
        assert second_response.status_code == 400
        assert "Студент уже записан на этот курс" in second_response.json()["detail"]
        print("Обработана дублирующая запись")

    def test_get_detailed_enrollments_empty(self):
        response = client.get("/api/enrollments/detailed/")

        assert response.status_code == 200
        data = response.json()
        assert data["enrollments"] == []
        print("Обработан пустой список детальных записей")

    def test_delete_enrollment_success(self):
        student_id, course_id = self.create_test_data()
        enrollment_data = {"student_id": student_id, "course_id": course_id}
        create_response = client.post("/api/enroll/", json=enrollment_data)
        enrollment_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/enrollments/{enrollment_id}")

        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Enrollment deleted successfully"

        print(f"Запись с ID: {enrollment_id} deleted")


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


    def test_courses_page(self):
        """Страница курсов"""
        response = client.get("/courses")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


    def test_enrollment_page(self):
        response = client.get("/enrollments")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


    def test_api_documentation(self):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestErrorCases:
    """Тест ощибок"""

    def test_invalid_json(self):
        """Тест отправки невалидного JSON"""
        response = client.post(
            "/api/students/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
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


    def test_health_check(self):
        response = client.get("/api/health/")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
        assert "version" in data
        assert "database" in data


    def test_malformed_enrollment_data(self):
        malformed_enrollment_data = {
            "student_id": "not_a_number",
            "course_id": "not_a_number",
        }

        response = client.post("/api/enroll/", json=malformed_enrollment_data)

        assert response.status_code == 422


class TestIntegration:
    def test_complete_flow(self):
        """Полный цикл работы системы"""
        student_data = {
            "first_name": "Integration",
            "last_name": "Test",
            "age": 22,
            "email": "integration@test.com",
        }
        student_response = client.post("/api/students/", json=student_data)
        assert student_response.status_code == 200
        student_id = student_response.json()["id"]

        course_data = {
            "title": "Integration",
            "description": "Test course for integration test",
            "duration_hours": 64,
            "price": 5000.0,
        }
        course_response = client.post("/api/courses/", json=course_data)
        assert course_response.status_code == 200
        course_id = course_response.json()["id"]

        enrollment_data = {
            "student_id": student_id,
            "course_id": course_id,
        }
        enrollment_response = client.post("/api/enroll/", json=enrollment_data)
        assert enrollment_response.status_code == 200
        enrollment_id = enrollment_response.json()["id"]

        enrollments_response = client.get("/api/enrollments/")
        assert enrollments_response.status_code == 200
        enrollments = enrollments_response.json()
        assert len(enrollments) == 1
        assert enrollments[0]["id"] == enrollment_id

        detailed_response = client.get("/api/enrollments/detailed/")
        assert detailed_response.status_code == 200
        detailed_data = detailed_response.json()
        assert len(detailed_data["enrollments"]) == 1

        enrollment_detail = detailed_data["enrollments"][0]
        assert enrollment_detail["enrollment"]["id"] == enrollment_id
        assert enrollment_detail["course"]["id"] == course_id
        assert enrollment_detail["student"]["id"] == student_id

        delete_response = client.delete(f"/api/enrollments/{enrollment_id}")
        assert delete_response.status_code == 200

        final_enrollments = client.get("/api/enrollments/").json()
        assert len(final_enrollments) == 0



if __name__ == "__main__":
    # Запуск тестов напрямую (альтернатива pytest)
    pytest.main([__file__, "-v"])
