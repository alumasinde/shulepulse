from sqlalchemy import or_,select
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.models.user import User

def authenticate(db:Session,school,email,phone,password):
    identity=email or phone
    if not identity:return None
    user=db.scalar(select(User).where(User.school_id==school.id,or_(User.email==identity,User.phone==identity),User.is_active.is_(True)))
    return user if user and verify_password(password,user.password_hash) else None
