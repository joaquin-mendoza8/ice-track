"""Order date attribute added

Revision ID: e1a42024da68
Revises: 8ddbdf9185fe
Create Date: 2024-11-25 13:47:54.028888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1a42024da68'
down_revision = '8ddbdf9185fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.Date(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('order_date')

    # ### end Alembic commands ###