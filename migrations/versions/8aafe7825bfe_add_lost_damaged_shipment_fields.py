"""Add lost/damaged shipment fields

Revision ID: 8aafe7825bfe
Revises: c3f131d5efd6
Create Date: 2024-11-24 20:45:32.858550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8aafe7825bfe'
down_revision = 'c3f131d5efd6'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns with default values to avoid integrity errors
    with op.batch_alter_table('shipment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lost_or_damaged', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('problem_description', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('shipping_vendor', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('damage_cost', sa.Float(), nullable=True))

    # Remove the server default after the table is updated
    # op.alter_column('shipment', 'lost_or_damaged', server_default=None)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shipment', schema=None) as batch_op:
        batch_op.drop_column('damage_cost')
        batch_op.drop_column('shipping_vendor')
        batch_op.drop_column('problem_description')
        batch_op.drop_column('lost_or_damaged')

    # ### end Alembic commands ###