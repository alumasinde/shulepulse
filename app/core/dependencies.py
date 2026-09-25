from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.tenant import get_current_school
from app.db.session import SessionLocal
from app.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_school(request: Request, db: Session = Depends(get_db)):
    school = get_current_school(request.headers.get("host", ""), db)
    if not school:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A school workspace is required")
    return school


def require_user(
    request: Request,
    school=Depends(require_school),
    db: Session = Depends(get_db),
):
    token = request.cookies.get(settings.cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
        token_school_id = int(payload["school_id"])
        if payload.get("type") != "access":
            raise ValueError("wrong token type")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    if token_school_id != school.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid tenant session")

    user = db.scalar(
        select(User).where(
            User.id == user_id,
            User.school_id == school.id,
            User.is_active.is_(True),
        )
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized")
    return user


def require_admin(user=Depends(require_user)):
    if user.role.lower() not in {"admin", "school_admin", "director"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return user
