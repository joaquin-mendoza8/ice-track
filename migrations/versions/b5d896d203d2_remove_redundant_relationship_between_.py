"""Remove redundant relationship between order and product

Revision ID: b5d896d203d2
Revises: 971ae563c309
Create Date: 2024-11-19 16:41:41.581041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5d896d203d2'
down_revision = '971ae563c309'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint('fk_order_product', type_='foreignkey')
        batch_op.drop_column('product_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key('fk_order_product', 'product', ['product_id'], ['id'])

    # ### end Alembic commands ###
