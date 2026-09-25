from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_school, require_user
from app.models.student import Parent, StudentParent

router = APIRouter(prefix="/parents", tags=["parents"])

def page(request, template, **ctx):
    return request.app.state.templates.TemplateResponse(template, {"request": request, **ctx})

@router.get("", response_class=HTMLResponse)
def index(request: Request, q: str = "", db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    stmt = select(Parent).where(Parent.school_id == school.id)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where((Parent.first_name.like(like)) | (Parent.last_name.like(like)) | (Parent.phone.like(like)))
    parents = db.scalars(stmt.order_by(Parent.first_name, Parent.last_name)).all()
    counts = {p.id: db.scalar(select(__import__('sqlalchemy').func.count(StudentParent.id)).where(StudentParent.parent_id == p.id, StudentParent.school_id == school.id)) or 0 for p in parents}
    return page(request, "parents/index.html", school=school, user=user, parents=parents, q=q, counts=counts, error=None)

@router.post("")
def create(request: Request, first_name: str = Form(...), last_name: str = Form(...), phone: str = Form(...),
           alternative_phone: str = Form(""), email: str = Form(""), address: str = Form(""), occupation: str = Form(""),
           db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    try:
        db.add(Parent(school_id=school.id, first_name=first_name.strip(), last_name=last_name.strip(), phone=phone.strip(),
                      alternative_phone=alternative_phone.strip() or None, email=email.strip().lower() or None,
                      address=address.strip() or None, occupation=occupation.strip() or None))
        db.commit()
    except IntegrityError:
        db.rollback()
        parents = db.scalars(select(Parent).where(Parent.school_id == school.id).order_by(Parent.first_name, Parent.last_name)).all()
        counts = {p.id: 0 for p in parents}
        return page(request, "parents/index.html", school=school, user=user, parents=parents, q="", counts=counts,
                    error="A parent with that phone number already exists in this school."), 400
    return RedirectResponse("/parents", status_code=303)
