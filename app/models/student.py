from datetime import date, datetime
from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Student(Base):
    __tablename__ = 'students'
    __table_args__ = (UniqueConstraint('school_id','admission_number',name='uq_student_school_admission'),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    admission_number: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    other_name: Mapped[str | None] = mapped_column(String(100))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(50))
    nationality: Mapped[str | None] = mapped_column(String(100), default='Kenyan')
    photo_url: Mapped[str | None] = mapped_column(String(500))
    class_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('classes.id', ondelete='SET NULL'), index=True)
    stream_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('streams.id', ondelete='SET NULL'), index=True)
    admission_date: Mapped[date | None] = mapped_column(Date)
    previous_school: Mapped[str | None] = mapped_column(String(255))
    student_status: Mapped[str] = mapped_column(String(50), nullable=False, default='active')
    address: Mapped[str | None] = mapped_column(String(500))
    city: Mapped[str | None] = mapped_column(String(100))
    county: Mapped[str | None] = mapped_column(String(100))
    birth_certificate_number: Mapped[str | None] = mapped_column(String(100))
    medical_notes: Mapped[str | None] = mapped_column(String(1000))
    allergies: Mapped[str | None] = mapped_column(String(1000))
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    parents = relationship('StudentParent', back_populates='student', cascade='all, delete-orphan')

class Parent(Base):
    __tablename__ = 'parents'
    __table_args__ = (UniqueConstraint('school_id','phone',name='uq_parent_school_phone'),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    alternative_phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(500))
    occupation: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    students = relationship('StudentParent', back_populates='parent', cascade='all, delete-orphan')

class StudentParent(Base):
    __tablename__ = 'student_parents'
    __table_args__ = (UniqueConstraint('student_id','parent_id',name='uq_student_parent'),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('parents.id', ondelete='CASCADE'), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False, default='parent')
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    student = relationship('Student', back_populates='parents')
    parent = relationship('Parent', back_populates='students')
