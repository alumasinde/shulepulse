from app.models.school import School
from app.models.user import User
from app.models.academic import AcademicYear, Term, ClassRoom, Stream, Subject, Teacher, TeacherAssignment, ClassSubject
from app.models.student import Student, Parent, StudentParent

__all__ = [
    'School','User','AcademicYear','Term','ClassRoom','Stream','Subject',
    'Teacher','TeacherAssignment','ClassSubject','Student','Parent','StudentParent'
]
