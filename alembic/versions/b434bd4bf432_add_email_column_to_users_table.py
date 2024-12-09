"""Add email column to users table

Revision ID: b434bd4bf432
Revises: 
Create Date: 2024-12-09 16:00:04.811294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b434bd4bf432'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_preferences_id', table_name='preferences')
    op.drop_table('preferences')
    op.drop_index('ix_animes_id', table_name='animes')
    op.drop_index('ix_animes_title', table_name='animes')
    op.drop_table('animes')
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'email')
    op.create_table('animes',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('genre', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='animes_pkey')
    )
    op.create_index('ix_animes_title', 'animes', ['title'], unique=False)
    op.create_index('ix_animes_id', 'animes', ['id'], unique=False)
    op.create_table('preferences',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('genre', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='preferences_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='preferences_pkey')
    )
    op.create_index('ix_preferences_id', 'preferences', ['id'], unique=False)
    # ### end Alembic commands ###