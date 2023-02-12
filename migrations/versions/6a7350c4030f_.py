"""empty message

Revision ID: 6a7350c4030f
Revises: 
Create Date: 2023-02-13 01:26:04.054854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a7350c4030f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('seeking_description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seeking_description', sa.VARCHAR(length=120), autoincrement=False, nullable=True))

    # ### end Alembic commands ###