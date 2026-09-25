from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class AcademicYear(Base):
    __tablename__ = 'academic_years'
    __table_args__ = (UniqueConstraint('school_id','name',name='uq_academic_year_school_name'),)
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    terms = relationship('Term', back_populates='academic_year', cascade='all, delete-orphan')

class Term(Base):
    __tablename__ = 'terms'
    __table_args__ = (UniqueConstraint('academic_year_id','name',name='uq_term_year_name'),)
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    academic_year_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    academic_year = relationship('AcademicYear', back_populates='terms')

class ClassRoom(Base):
    __tablename__ = 'classes'
    __table_args__ = (UniqueConstraint('school_id','name',name='uq_class_school_name'),)
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    streams = relationship('Stream', back_populates='class_room', cascade='all, delete-orphan')

class Stream(Base):
    __tablename__ = 'streams'
    __table_args__ = (UniqueConstraint('class_id','name',name='uq_stream_class_name'),)
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('classes.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    room: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    class_room = relationship('ClassRoom', back_populates='streams')

class Subject(Base):
    __tablename__ = 'subjects'
    __table_args__ = (UniqueConstraint('school_id','code',name='uq_subject_school_code'), UniqueConstraint('school_id','name',name='uq_subject_school_name'))
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class Teacher(Base):
    __tablename__ = 'teachers'
    __table_args__ = (UniqueConstraint('school_id','employee_number',name='uq_teacher_school_employee'),)
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(BIGINT(unsigned=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    employee_number: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    hire_date: Mapped[date | None] = mapped_column(Date)
    specialization: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class TeacherAssignment(Base):
    __tablename__ = 'teacher_assignments'
    __table_args__ = (UniqueConstraint('school_id','teacher_id','class_id','subject_id','academic_year_id',name='uq_teacher_assignment'),)
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    teacher_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('classes.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    academic_year_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ClassSubject(Base):
    __tablename__ = 'class_subjects'
    __table_args__ = (UniqueConstraint('school_id', 'class_id', 'subject_id', 'academic_year_id', name='uq_class_subject_year'),)
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('schools.id', ondelete='CASCADE'), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('classes.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    academic_year_id: Mapped[int] = mapped_column(BIGINT(unsigned=True), ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False, index=True)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    class_room = relationship('ClassRoom')
    subject = relationship('Subject')
    academic_year = relationship('AcademicYear')
