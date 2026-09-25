from datetime import datetime
from sqlalchemy import Boolean,DateTime,ForeignKey,String,UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
class User(Base):
    __tablename__='users'; __table_args__=(UniqueConstraint('school_id','email',name='uq_users_school_email'),UniqueConstraint('school_id','phone',name='uq_users_school_phone'))
    id:Mapped[int]=mapped_column(BIGINT(unsigned=True),primary_key=True,autoincrement=True)
    school_id:Mapped[int]=mapped_column(BIGINT(unsigned=True),ForeignKey('schools.id',ondelete='CASCADE'),nullable=False,index=True)
    first_name:Mapped[str]=mapped_column(String(100),nullable=False); last_name:Mapped[str]=mapped_column(String(100),nullable=False)
    email:Mapped[str|None]=mapped_column(String(255)); phone:Mapped[str|None]=mapped_column(String(30))
    password_hash:Mapped[str]=mapped_column(String(255),nullable=False); role:Mapped[str]=mapped_column(String(50),nullable=False)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,nullable=False); updated_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
    school=relationship('School',back_populates='users')
