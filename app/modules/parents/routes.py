from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_school, require_user
from app.models.student import Parent, Student, StudentParent
router=APIRouter(prefix='/parents',tags=['parents'])
def page(request,template,**ctx): return request.app.state.templates.TemplateResponse(template,{'request':request,**ctx})
@router.get('',response_class=HTMLResponse)
def index(request:Request,db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    parents=db.scalars(select(Parent).where(Parent.school_id==school.id).order_by(Parent.first_name,Parent.last_name)).all()
    return page(request,'parents/index.html',school=school,user=user,parents=parents)
@router.post('')
def create(first_name:str=Form(...),last_name:str=Form(...),phone:str=Form(...),alternative_phone:str=Form(''),email:str=Form(''),address:str=Form(''),occupation:str=Form(''),db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    db.add(Parent(school_id=school.id,first_name=first_name.strip(),last_name=last_name.strip(),phone=phone.strip(),alternative_phone=alternative_phone.strip() or None,email=email.strip().lower() or None,address=address.strip() or None,occupation=occupation.strip() or None)); db.commit(); return RedirectResponse('/parents',status_code=303)
