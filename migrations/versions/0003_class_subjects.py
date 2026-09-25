from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0003_class_subjects"
down_revision = "0002_academics_people"
branch_labels = None
depends_on = None

BIG = mysql.BIGINT(unsigned=True)

def upgrade():
    op.create_table(
        "class_subjects",
        sa.Column("id", BIG, primary_key=True, autoincrement=True),
        sa.Column("school_id", BIG, nullable=False),
        sa.Column("class_id", BIG, nullable=False),
        sa.Column("subject_id", BIG, nullable=False),
        sa.Column("academic_year_id", BIG, nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_years.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("school_id", "class_id", "subject_id", "academic_year_id", name="uq_class_subject_year"),
    )
    for col in ["school_id", "class_id", "subject_id", "academic_year_id"]:
        op.create_index(f"ix_class_subjects_{col}", "class_subjects", [col])

def downgrade():
    op.drop_table("class_subjects")
