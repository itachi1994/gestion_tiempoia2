"""Add priority column to task

Revision ID: d0487c7d9da3
Revises: a894bfbf3017
Create Date: 2025-05-01 10:54:11.949482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0487c7d9da3'
down_revision = 'a894bfbf3017'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('course_load_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('subjects_id', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('subjects_id')
        batch_op.drop_column('course_load_id')
        batch_op.drop_column('priority')

    # ### end Alembic commands ###
