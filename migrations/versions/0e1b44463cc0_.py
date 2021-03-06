"""empty message

Revision ID: 0e1b44463cc0
Revises: 6e0d84607cab
Create Date: 2019-08-01 10:44:19.174357

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e1b44463cc0'
down_revision = '6e0d84607cab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('analytics_data')
    op.add_column('enquiries', sa.Column('confirmation_email_task_id', sa.String(length=64), nullable=True))
    op.add_column('enquiries', sa.Column('copy_email_task_id', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('enquiries', 'copy_email_task_id')
    op.drop_column('enquiries', 'confirmation_email_task_id')
    op.create_table('analytics_data',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('url', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('user_agent', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('view_args', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('status_code', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('path', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('latency', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('request', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('url_args', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('ua_browser', sa.VARCHAR(length=16), autoincrement=False, nullable=True),
    sa.Column('ua_language', sa.VARCHAR(length=16), autoincrement=False, nullable=True),
    sa.Column('ua_platform', sa.VARCHAR(length=16), autoincrement=False, nullable=True),
    sa.Column('ua_version', sa.VARCHAR(length=16), autoincrement=False, nullable=True),
    sa.Column('referer', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('uuid', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='analytics_data_pkey')
    )
    # ### end Alembic commands ###
