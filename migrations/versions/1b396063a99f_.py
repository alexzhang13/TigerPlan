"""empty message

Revision ID: 1b396063a99f
Revises: f83c9349cf91
Create Date: 2022-03-25 18:48:03.082567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b396063a99f'
down_revision = 'f83c9349cf91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invitation_timeblock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timeblock_id', sa.Integer(), nullable=True),
    sa.Column('invitation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['invitation_id'], ['invitations.id'], ),
    sa.ForeignKeyConstraint(['timeblock_id'], ['timeblocks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invitation_timeblock')
    # ### end Alembic commands ###