"""Update Order attributes, fix shipment attribute names

Revision ID: 8ddbdf9185fe
Revises: 5a54474731ce
Create Date: 2024-11-25 11:11:03.541335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ddbdf9185fe'
down_revision = '5a54474731ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expected_shipping_date', sa.Date(), nullable=False))
        batch_op.add_column(sa.Column('desired_receipt_date', sa.Date(), nullable=False))
        batch_op.add_column(sa.Column('status', sa.String(length=150), nullable=False))
        batch_op.add_column(sa.Column('payment_date', sa.Date(), nullable=True))
        batch_op.drop_column('shipping_date')

    with op.batch_alter_table('shipment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipment_boxes', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('shipment_type', sa.String(length=150), nullable=False))
        batch_op.drop_column('shippment_boxes')
        batch_op.drop_column('shippment_type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shipment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shippment_type', sa.VARCHAR(length=150), nullable=False))
        batch_op.add_column(sa.Column('shippment_boxes', sa.INTEGER(), nullable=False))
        batch_op.drop_column('shipment_type')
        batch_op.drop_column('shipment_boxes')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipping_date', sa.DATE(), nullable=False))
        batch_op.drop_column('payment_date')
        batch_op.drop_column('status')
        batch_op.drop_column('desired_receipt_date')
        batch_op.drop_column('expected_shipping_date')

    # ### end Alembic commands ###
