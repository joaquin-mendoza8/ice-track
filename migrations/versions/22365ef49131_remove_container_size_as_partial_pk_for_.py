"""Remove container_size as partial PK for product

Revision ID: 22365ef49131
Revises: 2de8535ecf45
Create Date: 2024-11-07 10:19:19.072416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22365ef49131'
down_revision = '2de8535ecf45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('container_size',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('container_size',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)

    # ### end Alembic commands ###
