"""Resolve circular dependency btw order item and allocation

Revision ID: 0af52e3231c5
Revises: 3cf734741272
Create Date: 2024-11-27 08:45:12.155700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0af52e3231c5'
down_revision = '3cf734741272'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.drop_constraint('fk_product_allocation_id', type_='foreignkey')
        batch_op.drop_column('product_allocation_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_allocation_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key('fk_product_allocation_id', 'product_allocation', ['product_allocation_id'], ['id'])

    # ### end Alembic commands ###
