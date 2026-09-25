from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_school, require_user
from app.models.student import Student, Parent, StudentParent
from app.models.academic import ClassRoom, Stream

router=APIRouter(prefix='/students',tags=['students'])
def page(request,template,**ctx): return request.app.state.templates.TemplateResponse(template,{'request':request,**ctx})

@router.get('',response_class=HTMLResponse)
def index(request:Request,q:str='',db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    stmt=select(Student).where(Student.school_id==school.id)
    if q.strip():
        like=f'%{q.strip()}%'; stmt=stmt.where((Student.first_name.like(like))|(Student.last_name.like(like))|(Student.admission_number.like(like)))
    students=db.scalars(stmt.order_by(Student.first_name,Student.last_name)).all()
    classes=db.scalars(select(ClassRoom).where(ClassRoom.school_id==school.id).order_by(ClassRoom.name)).all()
    return page(request,'students/index.html',school=school,user=user,students=students,classes=classes,q=q)

@router.get('/new',response_class=HTMLResponse)
def new(request:Request,db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    classes=db.scalars(select(ClassRoom).where(ClassRoom.school_id==school.id).order_by(ClassRoom.name)).all()
    streams=db.scalars(select(Stream).where(Stream.school_id==school.id).order_by(Stream.name)).all()
    return page(request,'students/form.html',school=school,user=user,classes=classes,streams=streams,error=None)

@router.post('')
def create(admission_number:str=Form(...),first_name:str=Form(...),last_name:str=Form(...),other_name:str=Form(''),date_of_birth:date|None=Form(None),gender:str=Form(''),nationality:str=Form('Kenyan'),class_id:int|None=Form(None),stream_id:int|None=Form(None),admission_date:date|None=Form(None),previous_school:str=Form(''),address:str=Form(''),city:str=Form(''),county:str=Form(''),birth_certificate_number:str=Form(''),medical_notes:str=Form(''),allergies:str=Form(''),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    student=Student(school_id=school.id,admission_number=admission_number.strip(),first_name=first_name.strip(),last_name=last_name.strip(),other_name=other_name.strip() or None,date_of_birth=date_of_birth,gender=gender.strip() or None,nationality=nationality.strip() or None,class_id=class_id,stream_id=stream_id,admission_date=admission_date,previous_school=previous_school.strip() or None,address=address.strip() or None,city=city.strip() or None,county=county.strip() or None,birth_certificate_number=birth_certificate_number.strip() or None,medical_notes=medical_notes.strip() or None,allergies=allergies.strip() or None,extra_data={})
    db.add(student); db.commit(); db.refresh(student); return RedirectResponse(f'/students/{student.id}',status_code=303)

@router.get('/{student_id}',response_class=HTMLResponse)
def detail(student_id:int,request:Request,db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    student=db.scalar(select(Student).where(Student.id==student_id,Student.school_id==school.id))
    if not student: return HTMLResponse('Student not found',status_code=404)
    links=db.scalars(select(StudentParent).where(StudentParent.student_id==student.id,StudentParent.school_id==school.id)).all()
    parents=[db.get(Parent,l.parent_id) for l in links]
    classes=db.scalars(select(ClassRoom).where(ClassRoom.school_id==school.id)).all()
    available_parents=db.scalars(select(Parent).where(Parent.school_id==school.id).order_by(Parent.first_name,Parent.last_name)).all()
    linked_ids={p.id for p in parents if p}
    available_parents=[p for p in available_parents if p.id not in linked_ids]
    return page(request,'students/detail.html',school=school,user=user,student=student,parents=parents,classes=classes,available_parents=available_parents)

@router.post('/{student_id}/parents')
def link_parent(student_id:int,parent_id:int=Form(...),relationship_type:str=Form('parent'),is_primary:bool=Form(False),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    student=db.scalar(select(Student).where(Student.id==student_id,Student.school_id==school.id))
    parent=db.scalar(select(Parent).where(Parent.id==parent_id,Parent.school_id==school.id))
    if student and parent:
        exists=db.scalar(select(StudentParent).where(StudentParent.student_id==student.id,StudentParent.parent_id==parent.id))
        if not exists:
            db.add(StudentParent(school_id=school.id,student_id=student.id,parent_id=parent.id,relationship_type=relationship_type.strip() or 'parent',is_primary=is_primary)); db.commit()
    return RedirectResponse(f'/students/{student_id}',status_code=303)
