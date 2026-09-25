from fastapi import APIRouter,Depends,Form,Request,status
from fastapi.responses import HTMLResponse,RedirectResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.dependencies import get_db,require_school,require_user
from app.core.security import create_access_token
from app.modules.auth.service import authenticate
router=APIRouter()
@router.get('/login',response_class=HTMLResponse)
def login_page(request:Request,school=Depends(require_school)): return request.app.state.templates.TemplateResponse('auth/login.html',{'request':request,'school':school,'error':None})
@router.post('/login',response_class=HTMLResponse)
def login(request:Request,identifier:str=Form(...),password:str=Form(...),db:Session=Depends(get_db),school=Depends(require_school)):
    value=identifier.strip(); email=value.lower() if '@' in value else None; phone=value if email is None else None; user=authenticate(db,school,email,phone,password)
    if not user:return request.app.state.templates.TemplateResponse('auth/login.html',{'request':request,'school':school,'error':'Invalid login details.'},status_code=401)
    response=RedirectResponse('/dashboard',status_code=303); response.set_cookie(settings.cookie_name,create_access_token(user_id=user.id,school_id=school.id),httponly=True,secure=settings.cookie_secure,samesite=settings.cookie_samesite,max_age=settings.access_token_expire_minutes*60,path='/'); return response
@router.post('/logout')
def logout():
    response=RedirectResponse('/login',status_code=303); response.delete_cookie(settings.cookie_name,path='/'); return response
@router.get('/me')
def me(school=Depends(require_school),user=Depends(require_user)): return {'id':user.id,'school_id':school.id,'first_name':user.first_name,'last_name':user.last_name,'email':user.email,'phone':user.phone,'role':user.role}
