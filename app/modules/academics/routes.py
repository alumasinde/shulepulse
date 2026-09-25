from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db, require_school, require_user
from app.models.academic import AcademicYear, Term, ClassRoom, Stream, Subject, ClassSubject

router = APIRouter(prefix="/academics", tags=["academics"])


def page(request, template, **ctx):
    return request.app.state.templates.TemplateResponse(template, {"request": request, **ctx})


def year_overlaps(db: Session, school_id: int, starts_on: date, ends_on: date, exclude_id: int | None = None) -> bool:
    stmt = select(AcademicYear.id).where(
        AcademicYear.school_id == school_id,
        AcademicYear.starts_on <= ends_on,
        AcademicYear.ends_on >= starts_on,
    )
    if exclude_id:
        stmt = stmt.where(AcademicYear.id != exclude_id)
    return db.scalar(stmt.limit(1)) is not None


def term_overlaps(db: Session, school_id: int, academic_year_id: int, starts_on: date, ends_on: date, exclude_id: int | None = None) -> bool:
    stmt = select(Term.id).where(
        Term.school_id == school_id,
        Term.academic_year_id == academic_year_id,
        Term.starts_on <= ends_on,
        Term.ends_on >= starts_on,
    )
    if exclude_id:
        stmt = stmt.where(Term.id != exclude_id)
    return db.scalar(stmt.limit(1)) is not None


def load_context(db: Session, school_id: int):
    years = db.scalars(
        select(AcademicYear)
        .where(AcademicYear.school_id == school_id)
        .options(joinedload(AcademicYear.terms))
        .order_by(AcademicYear.starts_on.desc())
    ).unique().all()
    classes = db.scalars(
        select(ClassRoom)
        .where(ClassRoom.school_id == school_id)
        .options(joinedload(ClassRoom.streams))
        .order_by(ClassRoom.name)
    ).unique().all()
    subjects = db.scalars(
        select(Subject).where(Subject.school_id == school_id).order_by(Subject.name)
    ).all()
    active_year = next((y for y in years if y.is_active), None)
    assignments = []
    if active_year:
        assignments = db.scalars(
            select(ClassSubject)
            .where(ClassSubject.school_id == school_id, ClassSubject.academic_year_id == active_year.id)
            .options(joinedload(ClassSubject.class_room), joinedload(ClassSubject.subject))
            .order_by(ClassSubject.class_id, ClassSubject.subject_id)
        ).unique().all()
    term_count = sum(len(y.terms) for y in years)
    return years, classes, subjects, active_year, assignments, term_count


def render_index(request, db, school, user, error=None, success=None, status_code=200):
    years, classes, subjects, active_year, assignments, term_count = load_context(db, school.id)
    response = page(
        request,
        "academics/index.html",
        school=school,
        user=user,
        years=years,
        classes=classes,
        subjects=subjects,
        active_year=active_year,
        assignments=assignments,
        term_count=term_count,
        error=error,
        success=success,
    )
    response.status_code = status_code
    return response


@router.get("", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    return render_index(request, db, school, user)


@router.post("/years")
def create_year(
    request: Request,
    name: str = Form(...),
    starts_on: date = Form(...),
    ends_on: date = Form(...),
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    name = name.strip()
    if not name:
        return render_index(request, db, school, user, "Academic year name is required.", status_code=400)
    if ends_on <= starts_on:
        return render_index(request, db, school, user, "Academic year end date must be after its start date.", status_code=400)
    if year_overlaps(db, school.id, starts_on, ends_on):
        return render_index(request, db, school, user, "This academic year overlaps an existing academic year.", status_code=400)
    try:
        db.add(AcademicYear(school_id=school.id, name=name, starts_on=starts_on, ends_on=ends_on, is_active=False))
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_index(request, db, school, user, "That academic year already exists.", status_code=400)
    return RedirectResponse("/academics#years", status_code=303)


@router.post("/years/{year_id}/activate")
def activate_year(
    year_id: int,
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    target = db.scalar(select(AcademicYear).where(AcademicYear.id == year_id, AcademicYear.school_id == school.id))
    if not target:
        return RedirectResponse("/academics#years", status_code=303)
    db.query(AcademicYear).filter(AcademicYear.school_id == school.id).update({AcademicYear.is_active: False}, synchronize_session=False)
    db.query(Term).filter(Term.school_id == school.id).update({Term.is_active: False}, synchronize_session=False)
    target.is_active = True
    db.commit()
    return RedirectResponse("/academics#years", status_code=303)


@router.post("/terms")
def create_term(
    request: Request,
    academic_year_id: int = Form(...),
    name: str = Form(...),
    starts_on: date = Form(...),
    ends_on: date = Form(...),
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    year = db.scalar(select(AcademicYear).where(AcademicYear.id == academic_year_id, AcademicYear.school_id == school.id))
    if not year:
        return render_index(request, db, school, user, "Selected academic year was not found.", status_code=404)
    name = name.strip()
    if not name:
        return render_index(request, db, school, user, "Term name is required.", status_code=400)
    if ends_on <= starts_on:
        return render_index(request, db, school, user, "Term end date must be after its start date.", status_code=400)
    if starts_on < year.starts_on or ends_on > year.ends_on:
        return render_index(request, db, school, user, "The term dates must stay within the selected academic year.", status_code=400)
    if term_overlaps(db, school.id, year.id, starts_on, ends_on):
        return render_index(request, db, school, user, "This term overlaps another term in the same academic year.", status_code=400)
    try:
        db.add(Term(school_id=school.id, academic_year_id=year.id, name=name, starts_on=starts_on, ends_on=ends_on, is_active=False))
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_index(request, db, school, user, "That term already exists for this academic year.", status_code=400)
    return RedirectResponse("/academics#terms", status_code=303)


@router.post("/terms/{term_id}/activate")
def activate_term(
    term_id: int,
    request: Request,
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    target = db.scalar(
        select(Term).where(Term.id == term_id, Term.school_id == school.id).options(joinedload(Term.academic_year))
    )
    if not target:
        return RedirectResponse("/academics#terms", status_code=303)
    if not target.academic_year.is_active:
        return render_index(request, db, school, user, "Activate this term's academic year first.", status_code=400)
    db.query(Term).filter(Term.school_id == school.id).update({Term.is_active: False}, synchronize_session=False)
    target.is_active = True
    db.commit()
    return RedirectResponse("/academics#terms", status_code=303)


@router.post("/classes")
def create_class(
    request: Request,
    name: str = Form(...),
    level: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    name = name.strip()
    if not name:
        return render_index(request, db, school, user, "Class name is required.", status_code=400)
    try:
        db.add(ClassRoom(school_id=school.id, name=name, level=level.strip() or None, description=description.strip() or None))
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_index(request, db, school, user, "That class already exists.", status_code=400)
    return RedirectResponse("/academics#classes", status_code=303)


@router.post("/classes/{class_id}/streams")
def create_stream(
    request: Request,
    class_id: int,
    name: str = Form(...),
    room: str = Form(""),
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    cls = db.scalar(select(ClassRoom).where(ClassRoom.id == class_id, ClassRoom.school_id == school.id))
    if not cls:
        return render_index(request, db, school, user, "Selected class was not found.", status_code=404)
    name = name.strip()
    if not name:
        return render_index(request, db, school, user, "Stream name is required.", status_code=400)
    try:
        db.add(Stream(school_id=school.id, class_id=cls.id, name=name, room=room.strip() or None))
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_index(request, db, school, user, "That stream already exists in this class.", status_code=400)
    return RedirectResponse("/academics#classes", status_code=303)


@router.post("/subjects")
def create_subject(
    request: Request,
    name: str = Form(...),
    code: str = Form(""),
    category: str = Form(""),
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    name = name.strip()
    code = code.strip().upper() or None
    if not name:
        return render_index(request, db, school, user, "Subject name is required.", status_code=400)
    try:
        db.add(Subject(school_id=school.id, name=name, code=code, category=category.strip() or None))
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_index(request, db, school, user, "That subject name or code already exists.", status_code=400)
    return RedirectResponse("/academics#subjects", status_code=303)


@router.post("/curriculum")
def assign_subject(
    request: Request,
    class_id: int = Form(...),
    subject_id: int = Form(...),
    academic_year_id: int = Form(...),
    is_required: bool = Form(False),
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    year = db.scalar(select(AcademicYear).where(AcademicYear.id == academic_year_id, AcademicYear.school_id == school.id))
    cls = db.scalar(select(ClassRoom).where(ClassRoom.id == class_id, ClassRoom.school_id == school.id, ClassRoom.is_active.is_(True)))
    subject = db.scalar(select(Subject).where(Subject.id == subject_id, Subject.school_id == school.id, Subject.is_active.is_(True)))
    if not year or not cls or not subject:
        return render_index(request, db, school, user, "The selected academic year, class, or subject is invalid.", status_code=400)
    if not year.is_active:
        return render_index(request, db, school, user, "Activate the academic year before assigning its curriculum.", status_code=400)
    try:
        db.add(ClassSubject(school_id=school.id, class_id=cls.id, subject_id=subject.id, academic_year_id=year.id, is_required=is_required))
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_index(request, db, school, user, "That subject is already assigned to this class for the selected year.", status_code=400)
    return RedirectResponse("/academics#curriculum", status_code=303)


@router.post("/curriculum/{assignment_id}/remove")
def remove_subject_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    school=Depends(require_school),
    user=Depends(require_user),
):
    assignment = db.scalar(select(ClassSubject).where(ClassSubject.id == assignment_id, ClassSubject.school_id == school.id))
    if assignment:
        db.delete(assignment)
        db.commit()
    return RedirectResponse("/academics#curriculum", status_code=303)
