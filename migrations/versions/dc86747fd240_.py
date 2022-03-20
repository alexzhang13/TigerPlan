"""empty message

Revision ID: dc86747fd240
Revises: 2ae144e7ce21
Create Date: 2022-03-19 22:46:23.603052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc86747fd240'
down_revision = '2ae144e7ce21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('groups_member_id_fkey', 'groups', type_='foreignkey')
    op.drop_column('groups', 'member_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('member_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('groups_member_id_fkey', 'groups', 'users', ['member_id'], ['id'])
    # ### end Alembic commands ###
