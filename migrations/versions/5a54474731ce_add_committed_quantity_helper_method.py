"""Add committed_quantity + helper method

Revision ID: 5a54474731ce
Revises: afd6d3e93536
Create Date: 2024-11-23 21:39:08.873908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a54474731ce'
down_revision = 'afd6d3e93536'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('committed_quantity', sa.Integer(), nullable=False, server_default='0'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('committed_quantity')

    # ### end Alembic commands ###
