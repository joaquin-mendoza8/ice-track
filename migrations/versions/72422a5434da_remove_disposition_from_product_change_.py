"""Remove disposition from product, change relationships

Revision ID: 72422a5434da
Revises: 0af52e3231c5
Create Date: 2024-11-27 13:50:24.660635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72422a5434da'
down_revision = '0af52e3231c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('disposition')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('disposition', sa.VARCHAR(length=150), nullable=True))

    # ### end Alembic commands ###