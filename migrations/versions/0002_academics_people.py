from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = "0002_academics_people"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


BIG = mysql.BIGINT(unsigned=True)

def upgrade():
    op.create_table(
        "academic_years",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("school_id", "name", name="uq_academic_year_school_name"),
    )
    op.create_index("ix_academic_years_school_id", "academic_years", ["school_id"])

    op.create_table(
        "terms",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("academic_year_id", BIG, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["academic_year_id"], ["academic_years.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("academic_year_id", "name", name="uq_term_year_name"),
    )
    op.create_index("ix_terms_school_id", "terms", ["school_id"])
    op.create_index("ix_terms_academic_year_id", "terms", ["academic_year_id"])

    op.create_table(
        "classes",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("level", sa.String(50)),
        sa.Column("description", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("school_id", "name", name="uq_class_school_name"),
    )
    op.create_index("ix_classes_school_id", "classes", ["school_id"])

    op.create_table(
        "streams",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("class_id", BIG, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("room", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("class_id", "name", name="uq_stream_class_name"),
    )
    op.create_index("ix_streams_school_id", "streams", ["school_id"])
    op.create_index("ix_streams_class_id", "streams", ["class_id"])

    op.create_table(
        "subjects",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("code", sa.String(50)),
        sa.Column("category", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("school_id", "code", name="uq_subject_school_code"),
        sa.UniqueConstraint("school_id", "name", name="uq_subject_school_name"),
    )
    op.create_index("ix_subjects_school_id", "subjects", ["school_id"])

    op.create_table(
        "teachers",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("user_id", BIG, nullable=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("employee_number", sa.String(100)),
        sa.Column("phone", sa.String(30)),
        sa.Column("email", sa.String(255)),
        sa.Column("hire_date", sa.Date()),
        sa.Column("specialization", sa.String(255)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint(
            "school_id", "employee_number", name="uq_teacher_school_employee"
        ),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_teachers_school_id", "teachers", ["school_id"])

    op.create_table(
        "teacher_assignments",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("teacher_id", BIG, nullable=False),
        sa.Column("class_id", BIG, nullable=False),
        sa.Column("subject_id", BIG, nullable=False),
        sa.Column("academic_year_id", BIG, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["academic_year_id"], ["academic_years.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "school_id",
            "teacher_id",
            "class_id",
            "subject_id",
            "academic_year_id",
            name="uq_teacher_assignment",
        ),
    )
    for col in ["teacher_id", "class_id", "subject_id", "academic_year_id"]:
        op.create_index(f"ix_teacher_assignments_{col}", "teacher_assignments", [col])

    op.create_table(
        "students",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("admission_number", sa.String(100), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("other_name", sa.String(100)),
        sa.Column("date_of_birth", sa.Date()),
        sa.Column("gender", sa.String(50)),
        sa.Column("nationality", sa.String(100), server_default="Kenyan"),
        sa.Column("photo_url", sa.String(500)),
        sa.Column("class_id", BIG, nullable=True),
        sa.Column("stream_id", BIG, nullable=True),
        sa.Column("admission_date", sa.Date()),
        sa.Column("previous_school", sa.String(255)),
        sa.Column(
            "student_status", sa.String(50), nullable=False, server_default="active"
        ),
        sa.Column("address", sa.String(500)),
        sa.Column("city", sa.String(100)),
        sa.Column("county", sa.String(100)),
        sa.Column("birth_certificate_number", sa.String(100)),
        sa.Column("medical_notes", sa.String(1000)),
        sa.Column("allergies", sa.String(1000)),
        sa.Column("extra_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["stream_id"], ["streams.id"], ondelete="SET NULL"),
        sa.UniqueConstraint(
            "school_id", "admission_number", name="uq_student_school_admission"
        ),
    )
    for col in ["school_id", "class_id", "stream_id"]:
        op.create_index(f"ix_students_{col}", "students", [col])

    op.create_table(
        "parents",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(30), nullable=False),
        sa.Column("alternative_phone", sa.String(30)),
        sa.Column("email", sa.String(255)),
        sa.Column("address", sa.String(500)),
        sa.Column("occupation", sa.String(150)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("school_id", "phone", name="uq_parent_school_phone"),
    )
    op.create_index("ix_parents_school_id", "parents", ["school_id"])

    op.create_table(
        "student_parents",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("student_id", BIG, nullable=False),
        sa.Column("parent_id", BIG, nullable=False),
        sa.Column(
            "relationship_type", sa.String(100), nullable=False, server_default="parent"
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["parents.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("student_id", "parent_id", name="uq_student_parent"),
    )
    for col in ["school_id", "student_id", "parent_id"]:
        op.create_index(f"ix_student_parents_{col}", "student_parents", [col])


def downgrade():
    op.drop_table("student_parents")
    op.drop_table("parents")
    op.drop_table("students")
    op.drop_table("teacher_assignments")
    op.drop_table("teachers")
    op.drop_table("subjects")
    op.drop_table("streams")
    op.drop_table("classes")
    op.drop_table("terms")
    op.drop_table("academic_years")
