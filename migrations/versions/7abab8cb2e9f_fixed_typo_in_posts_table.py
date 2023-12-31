"""Fixed typo in posts table

Revision ID: 7abab8cb2e9f
Revises: 627ae27f6e44
Create Date: 2023-08-16 14:14:32.117906

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7abab8cb2e9f'
down_revision = '627ae27f6e44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', sa.DateTime(), nullable=True))
        batch_op.drop_column('date_poted')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_poted', mysql.DATETIME(), nullable=True))
        batch_op.drop_column('date_posted')

    # ### end Alembic commands ###
