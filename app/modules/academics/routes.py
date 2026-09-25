from datetime import date
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_school, require_user
from app.models.academic import AcademicYear, Term, ClassRoom, Stream, Subject

router = APIRouter(prefix='/academics', tags=['academics'])

def page(request, template, **ctx):
    return request.app.state.templates.TemplateResponse(template, {'request': request, **ctx})

@router.get('', response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    years=db.scalars(select(AcademicYear).where(AcademicYear.school_id==school.id).order_by(AcademicYear.starts_on.desc())).all()
    classes=db.scalars(select(ClassRoom).where(ClassRoom.school_id==school.id).order_by(ClassRoom.name)).all()
    subjects=db.scalars(select(Subject).where(Subject.school_id==school.id).order_by(Subject.name)).all()
    return page(request,'academics/index.html',school=school,user=user,years=years,classes=classes,subjects=subjects)

@router.post('/years')
def create_year(name: str=Form(...), starts_on: date=Form(...), ends_on: date=Form(...), db: Session=Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    year=AcademicYear(school_id=school.id,name=name.strip(),starts_on=starts_on,ends_on=ends_on,is_active=False)
    db.add(year); db.commit(); return RedirectResponse('/academics',status_code=303)

@router.post('/years/{year_id}/activate')
def activate_year(year_id:int, db:Session=Depends(get_db), school=Depends(require_school), user=Depends(require_user)):
    years=db.scalars(select(AcademicYear).where(AcademicYear.school_id==school.id)).all()
    target=next((x for x in years if x.id==year_id),None)
    if not target: return RedirectResponse('/academics',status_code=303)
    for y in years: y.is_active=(y.id==target.id)
    db.commit(); return RedirectResponse('/academics',status_code=303)

@router.post('/terms')
def create_term(academic_year_id:int=Form(...),name:str=Form(...),starts_on:date=Form(...),ends_on:date=Form(...),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    year=db.scalar(select(AcademicYear).where(AcademicYear.id==academic_year_id,AcademicYear.school_id==school.id))
    if year:
        db.add(Term(school_id=school.id,academic_year_id=year.id,name=name.strip(),starts_on=starts_on,ends_on=ends_on,is_active=False)); db.commit()
    return RedirectResponse('/academics',status_code=303)

@router.post('/classes')
def create_class(name:str=Form(...),level:str=Form(''),description:str=Form(''),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    db.add(ClassRoom(school_id=school.id,name=name.strip(),level=level.strip() or None,description=description.strip() or None)); db.commit(); return RedirectResponse('/academics',status_code=303)

@router.post('/classes/{class_id}/streams')
def create_stream(class_id:int,name:str=Form(...),room:str=Form(''),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    cls=db.scalar(select(ClassRoom).where(ClassRoom.id==class_id,ClassRoom.school_id==school.id))
    if cls:
        db.add(Stream(school_id=school.id,class_id=cls.id,name=name.strip(),room=room.strip() or None)); db.commit()
    return RedirectResponse('/academics',status_code=303)

@router.post('/subjects')
def create_subject(name:str=Form(...),code:str=Form(''),category:str=Form(''),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    db.add(Subject(school_id=school.id,name=name.strip(),code=code.strip().upper() or None,category=category.strip() or None)); db.commit(); return RedirectResponse('/academics',status_code=303)
