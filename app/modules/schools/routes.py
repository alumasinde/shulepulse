from fastapi import APIRouter,Depends,Form,Request,status
from fastapi.responses import HTMLResponse,RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.dependencies import get_db,require_school,require_user
from app.core.config import settings
from app.modules.schools.schemas import SchoolRegisterRequest
from app.modules.schools.service import register_school
from app.models.student import Student, Parent
from app.models.academic import Teacher, ClassRoom
router=APIRouter()
@router.get('/register',response_class=HTMLResponse)
def register_page(request:Request): return request.app.state.templates.TemplateResponse('auth/register.html',{'request':request,'error':None})
@router.post('/register',response_class=HTMLResponse)
def register(request:Request,school_name:str=Form(...),slug:str=Form(...),first_name:str=Form(...),last_name:str=Form(...),email:str=Form(''),phone:str=Form(''),password:str=Form(...),db:Session=Depends(get_db)):
    try: school,_=register_school(db,SchoolRegisterRequest(school_name=school_name,slug=slug,first_name=first_name,last_name=last_name,email=email or None,phone=phone or None,password=password))
    except ValueError as exc: return request.app.state.templates.TemplateResponse('auth/register.html',{'request':request,'error':str(exc)},status_code=400)
    return RedirectResponse(f'http://{school.slug}.{settings.root_domain}:8000/login',status_code=status.HTTP_303_SEE_OTHER)
@router.get('/dashboard',response_class=HTMLResponse)
def dashboard(request:Request,db:Session=Depends(get_db),school=Depends(require_school),user=Depends(require_user)):
    counts={
        'students': db.scalar(select(func.count(Student.id)).where(Student.school_id==school.id)) or 0,
        'parents': db.scalar(select(func.count(Parent.id)).where(Parent.school_id==school.id)) or 0,
        'teachers': db.scalar(select(func.count(Teacher.id)).where(Teacher.school_id==school.id)) or 0,
        'classes': db.scalar(select(func.count(ClassRoom.id)).where(ClassRoom.school_id==school.id)) or 0,
    }
    return request.app.state.templates.TemplateResponse('dashboard/index.html',{'request':request,'school':school,'user':user,'counts':counts})
