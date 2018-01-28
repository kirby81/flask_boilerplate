"""Change username to nullable

Revision ID: 36681add907d
Revises: 020b8de65a95
Create Date: 2018-01-28 16:01:33.253861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36681add907d'
down_revision = '020b8de65a95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(length=80),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(length=80),
               nullable=False)
    # ### end Alembic commands ###
