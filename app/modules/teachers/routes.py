from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_school, require_user
from app.models.academic import Teacher
router=APIRouter(prefix='/teachers',tags=['teachers'])
def page(request,template,**ctx): return request.app.state.templates.TemplateResponse(template,{'request':request,**ctx})
@router.get('',response_class=HTMLResponse)
def index(request:Request,db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    teachers=db.scalars(select(Teacher).where(Teacher.school_id==school.id).order_by(Teacher.first_name,Teacher.last_name)).all()
    return page(request,'teachers/index.html',school=school,user=user,teachers=teachers)
@router.post('')
def create(first_name:str=Form(...),last_name:str=Form(...),employee_number:str=Form(''),phone:str=Form(''),email:str=Form(''),hire_date:date|None=Form(None),specialization:str=Form(''),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    db.add(Teacher(school_id=school.id,first_name=first_name.strip(),last_name=last_name.strip(),employee_number=employee_number.strip() or None,phone=phone.strip() or None,email=email.strip().lower() or None,hire_date=hire_date,specialization=specialization.strip() or None)); db.commit(); return RedirectResponse('/teachers',status_code=303)
