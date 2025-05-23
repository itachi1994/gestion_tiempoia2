"""RF13 - add WeeklySuggestion table

Revision ID: 978d2170c628
Revises: 31f009b37812
Create Date: 2025-04-30 11:03:06.917289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '978d2170c628'
down_revision = '31f009b37812'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weekly_suggestions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weekly_suggestions')
    # ### end Alembic commands ###
