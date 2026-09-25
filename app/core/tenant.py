from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.school import School

def extract_tenant_slug(host:str)->str|None:
    hostname=host.split(':',1)[0].lower().rstrip('.')
    root=settings.root_domain.lower().rstrip('.')
    if hostname in {'localhost','127.0.0.1',root}: return None
    suffix='.'+root
    if hostname.endswith(suffix):
        slug=hostname[:-len(suffix)].strip('.')
        return slug if slug and '.' not in slug else None
    return None

def get_current_school(host:str,db:Session):
    slug=extract_tenant_slug(host)
    if not slug:return None
    school=db.scalar(select(School).where(School.slug==slug,School.is_active.is_(True)))
    if not school: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='School workspace not found')
    return school
