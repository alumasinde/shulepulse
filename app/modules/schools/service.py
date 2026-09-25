from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_password
from app.models.school import School
from app.models.user import User

def register_school(db:Session,data):
    if db.scalar(select(School).where(School.slug==data.slug)): raise ValueError('That school handle is already registered')
    school=School(name=data.school_name.strip(),slug=data.slug,email=str(data.email) if data.email else None,phone=data.phone.strip() if data.phone else None,settings=settings.default_settings_dict)
    user=User(school=school,first_name=data.first_name.strip(),last_name=data.last_name.strip(),email=str(data.email) if data.email else None,phone=data.phone.strip() if data.phone else None,password_hash=hash_password(data.password),role='admin')
    db.add_all([school,user])
    try: db.commit()
    except IntegrityError: db.rollback(); raise ValueError('That school handle or admin contact is already registered')
    db.refresh(school); db.refresh(user); return school,user
