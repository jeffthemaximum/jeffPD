"""added next to Log

Revision ID: 18b4980d0b2
Revises: 1a0979e64941
Create Date: 2015-09-06 12:13:42.956606

"""

# revision identifiers, used by Alembic.
revision = '18b4980d0b2'
down_revision = '1a0979e64941'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('logs', sa.Column('next', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('logs', 'next')
    ### end Alembic commands ###
