"""New Migration

Revision ID: fa3b26ee7169
Revises: 
Create Date: 2021-09-29 07:20:15.369298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa3b26ee7169'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conservation_area',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('photos_path', sa.String(), nullable=True),
    sa.Column('region_path', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conservation_area_id'), 'conservation_area', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_conservation_area_id'), table_name='conservation_area')
    op.drop_table('conservation_area')
    # ### end Alembic commands ###