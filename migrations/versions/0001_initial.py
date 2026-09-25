from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

BIG = mysql.BIGINT(unsigned=True)
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table('schools',sa.Column('id',BIG,primary_key=True,autoincrement=True),sa.Column('name',sa.String(255),nullable=False),sa.Column('slug',sa.String(100),nullable=False),sa.Column('email',sa.String(255)),sa.Column('phone',sa.String(30)),sa.Column('settings',sa.JSON(),nullable=False),sa.Column('is_active',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('created_at',sa.DateTime(),nullable=False),sa.Column('updated_at',sa.DateTime(),nullable=False),sa.UniqueConstraint('slug',name='uq_schools_slug')); op.create_index('ix_schools_slug','schools',['slug'])
    op.create_table('users',sa.Column('id',BIG,primary_key=True,autoincrement=True),sa.Column('school_id',BIG,nullable=False),sa.Column('first_name',sa.String(100),nullable=False),sa.Column('last_name',sa.String(100),nullable=False),sa.Column('email',sa.String(255)),sa.Column('phone',sa.String(30)),sa.Column('password_hash',sa.String(255),nullable=False),sa.Column('role',sa.String(50),nullable=False),sa.Column('is_active',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('created_at',sa.DateTime(),nullable=False),sa.Column('updated_at',sa.DateTime(),nullable=False),sa.ForeignKeyConstraint(['school_id'],['schools.id'],ondelete='CASCADE'),sa.UniqueConstraint('school_id','email',name='uq_users_school_email'),sa.UniqueConstraint('school_id','phone',name='uq_users_school_phone')); op.create_index('ix_users_school_id','users',['school_id'])
def downgrade(): op.drop_table('users'); op.drop_table('schools')
