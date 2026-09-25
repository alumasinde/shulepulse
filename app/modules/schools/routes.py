from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.dependencies import get_db, require_school, require_user
from app.models.academic import AcademicYear, ClassRoom, Teacher, Term, Subject
from app.models.student import Parent, Student
from app.modules.schools.schemas import SchoolRegisterRequest
from app.modules.schools.service import register_school

router = APIRouter()


def page(request, template, **ctx):
    return request.app.state.templates.TemplateResponse(template, {"request": request, **ctx})


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return page(request, "auth/register.html", error=None)


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    school_name: str = Form(...), slug: str = Form(...), first_name: str = Form(...),
    last_name: str = Form(...), email: str = Form(""), phone: str = Form(""),
    password: str = Form(...), db: Session = Depends(get_db),
):
    try:
        school, _ = register_school(db, SchoolRegisterRequest(
            school_name=school_name, slug=slug, first_name=first_name, last_name=last_name,
            email=email or None, phone=phone or None, password=password,
        ))
    except ValueError as exc:
        return page(request, "auth/register.html", error=str(exc))
    return RedirectResponse(
        f"http://{school.slug}.{settings.root_domain}:8000/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    counts = {
        "students": db.scalar(select(func.count(Student.id)).where(Student.school_id == school.id)) or 0,
        "parents": db.scalar(select(func.count(Parent.id)).where(Parent.school_id == school.id)) or 0,
        "teachers": db.scalar(select(func.count(Teacher.id)).where(Teacher.school_id == school.id)) or 0,
        "classes": db.scalar(select(func.count(ClassRoom.id)).where(ClassRoom.school_id == school.id)) or 0,
        "subjects": db.scalar(select(func.count(Subject.id)).where(Subject.school_id == school.id)) or 0,
    }
    active_year = db.scalar(select(AcademicYear).where(AcademicYear.school_id == school.id, AcademicYear.is_active.is_(True)).order_by(AcademicYear.starts_on.desc()))
    active_term = None
    if active_year:
        active_term = db.scalar(select(Term).where(Term.school_id == school.id, Term.academic_year_id == active_year.id, Term.is_active.is_(True)))
    recent_students = db.scalars(select(Student).where(Student.school_id == school.id).order_by(Student.created_at.desc()).limit(6)).all()
    setup = {
        "academic_year": bool(active_year),
        "term": bool(active_term),
        "classes": counts["classes"] > 0,
        "subjects": counts["subjects"] > 0,
    }
    completed = sum(setup.values())
    return page(request, "dashboard/index.html", school=school, user=user, counts=counts,
                active_year=active_year, active_term=active_term, recent_students=recent_students,
                setup=setup, setup_completed=completed, setup_total=len(setup))
