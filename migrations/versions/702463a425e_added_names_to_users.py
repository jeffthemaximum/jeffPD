"""added names to users

Revision ID: 702463a425e
Revises: 456a945560f6
Create Date: 2015-08-23 12:47:01.032973

"""

# revision identifiers, used by Alembic.
revision = '702463a425e'
down_revision = '456a945560f6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('first_name', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    ### end Alembic commands ###