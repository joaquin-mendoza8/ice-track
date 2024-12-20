"""Add shipment_id to allocations

Revision ID: 45ce123f7def
Revises: d780eb48aa49
Create Date: 2024-12-02 00:18:21.645017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45ce123f7def'
down_revision = 'd780eb48aa49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_allocation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipment_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_shipment_id', 'shipment', ['shipment_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_allocation', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('shipment_id')

    # ### end Alembic commands ###
