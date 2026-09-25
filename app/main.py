import uuid
from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.modules.auth.routes import router as auth_router
from app.modules.schools.routes import router as school_router
from app.modules.academics.routes import router as academics_router
from app.modules.students.routes import router as students_router
from app.modules.parents.routes import router as parents_router
from app.modules.teachers.routes import router as teachers_router
app=FastAPI(title=settings.app_name,version='0.1.0',docs_url='/docs' if settings.debug else None,redoc_url='/redoc' if settings.debug else None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=settings.allowed_host_list)
app.mount('/static',StaticFiles(directory='static'),name='static')
app.state.templates=Jinja2Templates(directory='app/templates')
app.state.settings=settings
@app.middleware('http')
async def security(request:Request,call_next):
    rid=request.headers.get('X-Request-ID') or uuid.uuid4().hex; response=await call_next(request); response.headers['X-Request-ID']=rid; response.headers['X-Content-Type-Options']='nosniff'; response.headers['X-Frame-Options']='SAMEORIGIN'; response.headers['Referrer-Policy']='strict-origin-when-cross-origin'; return response
@app.get('/')
def home(request:Request): return app.state.templates.TemplateResponse('marketing/home.html',{'request':request})
@app.get('/health')
def health(): return {'status':'ok'}
app.include_router(school_router); app.include_router(auth_router); app.include_router(academics_router); app.include_router(students_router); app.include_router(parents_router); app.include_router(teachers_router)
