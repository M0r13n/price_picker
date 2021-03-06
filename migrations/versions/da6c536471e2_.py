"""empty message

Revision ID: da6c536471e2
Revises: 66ad5bfcaa78
Create Date: 2019-08-15 12:11:23.159436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da6c536471e2'
down_revision = '66ad5bfcaa78'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shops',
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('name'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shops')
    # ### end Alembic commands ###
