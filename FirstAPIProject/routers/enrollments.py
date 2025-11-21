from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import crud
from models import Enrollment, EnrollmentCreate

router = APIRouter(prefix="/api", tags=["enrollments"])

@router.post("/enroll/", response_model=Enrollment)
async def enroll_student(enrollment: EnrollmentCreate):
    """Записать студента на курс"""
    try:
        new_enrollment = crud.create_enrollment(enrollment)
        return new_enrollment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.get("/enrollments/", response_model=list[Enrollment])
async def get_enrollments():
    """Получить все записи на курсы"""
    enrollments = crud.get_all_enrollments()
    return enrollments

@router.get("/enrollments/detailed/")
async def get_detailed_enrollments():
    """Получить записи с информацией о студентах и курсах"""
    detailed_enrollments = crud.get_detailed_enrollments()
    return {"enrollments": detailed_enrollments}

@router.delete("/enrollments/{enrollment_id}")
async def delete_enrollment(enrollment_id: int):
    """Удалить запись по ID"""
    success = crud.delete_enrollment(enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"message": "Enrollment deleted successfully"}

@router.get("/page/", response_class=HTMLResponse, include_in_schema=False)
async def enrollments_page():
    try:
        with open("templates/enrollments.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Enrollments Page</h1><p>HTML file not found</p>")