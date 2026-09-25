from datetime import datetime
from sqlalchemy import BigInteger,Boolean,DateTime,JSON,String
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
class School(Base):
    __tablename__='schools'
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True,autoincrement=True)
    name:Mapped[str]=mapped_column(String(255),nullable=False)
    slug:Mapped[str]=mapped_column(String(100),unique=True,index=True,nullable=False)
    email:Mapped[str|None]=mapped_column(String(255)); phone:Mapped[str|None]=mapped_column(String(30))
    settings:Mapped[dict]=mapped_column(JSON,nullable=False,default=dict)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
    users=relationship('User',back_populates='school',cascade='all, delete-orphan')
