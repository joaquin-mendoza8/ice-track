"""Enrique

Revision ID: bcef467f219c
Revises: afd6d3e93536
Create Date: 2024-11-23 17:01:12.933554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcef467f219c'
down_revision = 'afd6d3e93536'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('shipping_date', sa.Date(), nullable=False))
        batch_op.add_column(sa.Column('shipping_address', sa.String(length=250), nullable=False))
        batch_op.alter_column('billing_address',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=250),
               existing_nullable=False)
        batch_op.create_foreign_key('fk_user_id', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('line_item_cost', sa.Float(), nullable=False))
        batch_op.drop_column('ship_date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ship_date', sa.DATE(), nullable=False))
        batch_op.drop_column('line_item_cost')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('billing_address',
               existing_type=sa.String(length=250),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.drop_column('shipping_address')
        batch_op.drop_column('shipping_date')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
