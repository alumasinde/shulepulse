from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_school, require_user
from app.models.student import Student, Parent, StudentParent
from app.models.academic import ClassRoom, Stream

router = APIRouter(prefix="/students", tags=["students"])


def page(request, template, **ctx):
    return request.app.state.templates.TemplateResponse(template, {"request": request, **ctx})


def load_placement(db, school_id, class_id, stream_id):
    cls = db.scalar(select(ClassRoom).where(ClassRoom.id == class_id, ClassRoom.school_id == school_id)) if class_id else None
    stream = db.scalar(select(Stream).where(Stream.id == stream_id, Stream.school_id == school_id)) if stream_id else None
    if class_id and not cls:
        raise ValueError("Selected class does not belong to this school")
    if stream_id and not stream:
        raise ValueError("Selected stream does not belong to this school")
    if stream and cls and stream.class_id != cls.id:
        raise ValueError("Selected stream does not belong to the selected class")
    return cls, stream


@router.get("", response_class=HTMLResponse)
def index(request: Request, q: str = "", db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    stmt = select(Student).where(Student.school_id == school.id)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where((Student.first_name.like(like)) | (Student.last_name.like(like)) | (Student.admission_number.like(like)))
    students = db.scalars(stmt.order_by(Student.first_name, Student.last_name)).all()
    return page(request, "students/index.html", school=school, user=user, students=students, q=q)


@router.get("/new", response_class=HTMLResponse)
def new(request: Request, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    classes = db.scalars(select(ClassRoom).where(ClassRoom.school_id == school.id, ClassRoom.is_active.is_(True)).order_by(ClassRoom.name)).all()
    streams = db.scalars(select(Stream).where(Stream.school_id == school.id, Stream.is_active.is_(True)).order_by(Stream.name)).all()
    return page(request, "students/form.html", school=school, user=user, classes=classes, streams=streams, error=None)


@router.post("")
def create(
    request: Request,
    admission_number: str = Form(...), first_name: str = Form(...), last_name: str = Form(...),
    other_name: str = Form(""), date_of_birth: date | None = Form(None), gender: str = Form(""),
    nationality: str = Form("Kenyan"), class_id: int | None = Form(None), stream_id: int | None = Form(None),
    admission_date: date | None = Form(None), previous_school: str = Form(""), address: str = Form(""),
    city: str = Form(""), county: str = Form(""), birth_certificate_number: str = Form(""),
    medical_notes: str = Form(""), allergies: str = Form(""), db: Session = Depends(get_db),
    school=Depends(require_school), user=Depends(require_user),
):
    try:
        load_placement(db, school.id, class_id, stream_id)
        student = Student(
            school_id=school.id, admission_number=admission_number.strip(), first_name=first_name.strip(),
            last_name=last_name.strip(), other_name=other_name.strip() or None, date_of_birth=date_of_birth,
            gender=gender.strip() or None, nationality=nationality.strip() or None, class_id=class_id,
            stream_id=stream_id, admission_date=admission_date, previous_school=previous_school.strip() or None,
            address=address.strip() or None, city=city.strip() or None, county=county.strip() or None,
            birth_certificate_number=birth_certificate_number.strip() or None,
            medical_notes=medical_notes.strip() or None, allergies=allergies.strip() or None, extra_data={},
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        classes = db.scalars(select(ClassRoom).where(ClassRoom.school_id == school.id, ClassRoom.is_active.is_(True)).order_by(ClassRoom.name)).all()
        streams = db.scalars(select(Stream).where(Stream.school_id == school.id, Stream.is_active.is_(True)).order_by(Stream.name)).all()
        error = "Admission number is already in use." if isinstance(exc, IntegrityError) else str(exc)
        return page(request, "students/form.html", school=school, user=user, classes=classes, streams=streams, error=error), 400
    return RedirectResponse(f"/students/{student.id}", status_code=303)


@router.get("/{student_id}/edit", response_class=HTMLResponse)
def edit_page(student_id: int, request: Request, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    student = db.scalar(select(Student).where(Student.id == student_id, Student.school_id == school.id))
    if not student:
        return HTMLResponse("Student not found", status_code=404)
    classes = db.scalars(select(ClassRoom).where(ClassRoom.school_id == school.id, ClassRoom.is_active.is_(True)).order_by(ClassRoom.name)).all()
    streams = db.scalars(select(Stream).where(Stream.school_id == school.id, Stream.is_active.is_(True)).order_by(Stream.name)).all()
    return page(request, "students/form.html", school=school, user=user, classes=classes, streams=streams, student=student, error=None)

@router.post("/{student_id}/edit")
def edit(
    student_id: int, request: Request, admission_number: str = Form(...), first_name: str = Form(...), last_name: str = Form(...),
    other_name: str = Form(""), date_of_birth: date | None = Form(None), gender: str = Form(""), nationality: str = Form("Kenyan"),
    class_id: int | None = Form(None), stream_id: int | None = Form(None), admission_date: date | None = Form(None),
    previous_school: str = Form(""), address: str = Form(""), city: str = Form(""), county: str = Form(""),
    birth_certificate_number: str = Form(""), medical_notes: str = Form(""), allergies: str = Form(""),
    student_status: str = Form("active"), db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user),
):
    student = db.scalar(select(Student).where(Student.id == student_id, Student.school_id == school.id))
    if not student:
        return HTMLResponse("Student not found", status_code=404)
    try:
        load_placement(db, school.id, class_id, stream_id)
        student.admission_number = admission_number.strip(); student.first_name = first_name.strip(); student.last_name = last_name.strip()
        student.other_name = other_name.strip() or None; student.date_of_birth = date_of_birth; student.gender = gender.strip() or None
        student.nationality = nationality.strip() or None; student.class_id = class_id; student.stream_id = stream_id
        student.admission_date = admission_date; student.previous_school = previous_school.strip() or None; student.address = address.strip() or None
        student.city = city.strip() or None; student.county = county.strip() or None; student.birth_certificate_number = birth_certificate_number.strip() or None
        student.medical_notes = medical_notes.strip() or None; student.allergies = allergies.strip() or None; student.student_status = student_status.strip() or "active"
        db.commit()
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        classes = db.scalars(select(ClassRoom).where(ClassRoom.school_id == school.id, ClassRoom.is_active.is_(True)).order_by(ClassRoom.name)).all()
        streams = db.scalars(select(Stream).where(Stream.school_id == school.id, Stream.is_active.is_(True)).order_by(Stream.name)).all()
        return page(request, "students/form.html", school=school, user=user, classes=classes, streams=streams, student=student, error="Admission number is already in use." if isinstance(exc, IntegrityError) else str(exc)), 400
    return RedirectResponse(f"/students/{student_id}", status_code=303)

@router.get("/{student_id}", response_class=HTMLResponse)
def detail(student_id: int, request: Request, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    student = db.scalar(select(Student).where(Student.id == student_id, Student.school_id == school.id))
    if not student:
        return HTMLResponse("Student not found", status_code=404)
    links = db.scalars(select(StudentParent).where(StudentParent.student_id == student.id, StudentParent.school_id == school.id)).all()
    parents = db.scalars(select(Parent).where(Parent.id.in_([x.parent_id for x in links]), Parent.school_id == school.id)).all() if links else []
    cls = db.scalar(select(ClassRoom).where(ClassRoom.id == student.class_id, ClassRoom.school_id == school.id)) if student.class_id else None
    stream = db.scalar(select(Stream).where(Stream.id == student.stream_id, Stream.school_id == school.id)) if student.stream_id else None
    available_parents = db.scalars(select(Parent).where(Parent.school_id == school.id).order_by(Parent.first_name, Parent.last_name)).all()
    linked_ids = {p.id for p in parents}
    available_parents = [p for p in available_parents if p.id not in linked_ids]
    return page(request, "students/detail.html", school=school, user=user, student=student, parents=parents,
                available_parents=available_parents, student_class=cls, student_stream=stream)


@router.post("/{student_id}/parents")
def link_parent(student_id: int, parent_id: int = Form(...), relationship_type: str = Form("parent"), is_primary: bool = Form(False),
                db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    student = db.scalar(select(Student).where(Student.id == student_id, Student.school_id == school.id))
    parent = db.scalar(select(Parent).where(Parent.id == parent_id, Parent.school_id == school.id))
    if not student or not parent:
        return HTMLResponse("Student or parent not found", status_code=404)
    exists = db.scalar(select(StudentParent).where(StudentParent.student_id == student.id, StudentParent.parent_id == parent.id, StudentParent.school_id == school.id))
    if not exists:
        if is_primary:
            db.query(StudentParent).filter(StudentParent.school_id == school.id, StudentParent.student_id == student.id).update({StudentParent.is_primary: False})
        db.add(StudentParent(school_id=school.id, student_id=student.id, parent_id=parent.id,
                             relationship_type=relationship_type.strip() or "parent", is_primary=is_primary))
        db.commit()
    return RedirectResponse(f"/students/{student_id}", status_code=303)
