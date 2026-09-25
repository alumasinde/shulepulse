from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_school, require_user
from app.models.academic import AcademicYear, Term, ClassRoom, Stream, Subject

router = APIRouter(prefix="/academics", tags=["academics"])

def page(request, template, **ctx):
    return request.app.state.templates.TemplateResponse(template, {"request": request, **ctx})

def render_index(request, db, school, user, error=None):
    years = db.scalars(select(AcademicYear).where(AcademicYear.school_id == school.id).order_by(AcademicYear.starts_on.desc())).all()
    classes = db.scalars(select(ClassRoom).where(ClassRoom.school_id == school.id).order_by(ClassRoom.name)).all()
    streams = db.scalars(select(Stream).where(Stream.school_id == school.id).order_by(Stream.name)).all()
    subjects = db.scalars(select(Subject).where(Subject.school_id == school.id).order_by(Subject.name)).all()
    return page(request, "academics/index.html", school=school, user=user, years=years, classes=classes, streams=streams, subjects=subjects, error=error)

@router.get("", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    return render_index(request, db, school, user)

@router.post("/years")
def create_year(request: Request, name: str = Form(...), starts_on: date = Form(...), ends_on: date = Form(...), db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    if ends_on <= starts_on:
        return render_index(request, db, school, user, "Academic year end date must be after its start date."), 400
    try:
        db.add(AcademicYear(school_id=school.id, name=name.strip(), starts_on=starts_on, ends_on=ends_on, is_active=False)); db.commit()
    except IntegrityError:
        db.rollback(); return render_index(request, db, school, user, "That academic year already exists."), 400
    return RedirectResponse("/academics", status_code=303)

@router.post("/years/{year_id}/activate")
def activate_year(year_id: int, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    target = db.scalar(select(AcademicYear).where(AcademicYear.id == year_id, AcademicYear.school_id == school.id))
    if target:
        for year in db.scalars(select(AcademicYear).where(AcademicYear.school_id == school.id)).all(): year.is_active = year.id == target.id
        db.commit()
    return RedirectResponse("/academics", status_code=303)

@router.post("/terms")
def create_term(request: Request, academic_year_id: int = Form(...), name: str = Form(...), starts_on: date = Form(...), ends_on: date = Form(...), db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    year = db.scalar(select(AcademicYear).where(AcademicYear.id == academic_year_id, AcademicYear.school_id == school.id))
    if not year: return render_index(request, db, school, user, "Selected academic year was not found."), 404
    if ends_on <= starts_on: return render_index(request, db, school, user, "Term end date must be after its start date."), 400
    try:
        db.add(Term(school_id=school.id, academic_year_id=year.id, name=name.strip(), starts_on=starts_on, ends_on=ends_on, is_active=False)); db.commit()
    except IntegrityError:
        db.rollback(); return render_index(request, db, school, user, "That term already exists for this academic year."), 400
    return RedirectResponse("/academics", status_code=303)

@router.post("/terms/{term_id}/activate")
def activate_term(term_id: int, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    target = db.scalar(select(Term).where(Term.id == term_id, Term.school_id == school.id))
    if target:
        for term in db.scalars(select(Term).where(Term.school_id == school.id, Term.academic_year_id == target.academic_year_id)).all(): term.is_active = term.id == target.id
        db.commit()
    return RedirectResponse("/academics", status_code=303)

@router.post("/classes")
def create_class(request: Request, name: str = Form(...), level: str = Form(""), description: str = Form(""), db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    try:
        db.add(ClassRoom(school_id=school.id, name=name.strip(), level=level.strip() or None, description=description.strip() or None)); db.commit()
    except IntegrityError:
        db.rollback(); return render_index(request, db, school, user, "That class already exists."), 400
    return RedirectResponse("/academics", status_code=303)

@router.post("/classes/{class_id}/streams")
def create_stream(request: Request, class_id: int, name: str = Form(...), room: str = Form(""), db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    cls = db.scalar(select(ClassRoom).where(ClassRoom.id == class_id, ClassRoom.school_id == school.id))
    if not cls: return render_index(request, db, school, user, "Selected class was not found."), 404
    try:
        db.add(Stream(school_id=school.id, class_id=cls.id, name=name.strip(), room=room.strip() or None)); db.commit()
    except IntegrityError:
        db.rollback(); return render_index(request, db, school, user, "That stream already exists in this class."), 400
    return RedirectResponse("/academics", status_code=303)

@router.post("/subjects")
def create_subject(request: Request, name: str = Form(...), code: str = Form(""), category: str = Form(""), db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    try:
        db.add(Subject(school_id=school.id, name=name.strip(), code=code.strip().upper() or None, category=category.strip() or None)); db.commit()
    except IntegrityError:
        db.rollback(); return render_index(request, db, school, user, "That subject name or code already exists."), 400
    return RedirectResponse("/academics", status_code=303)
