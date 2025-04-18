"""add templates table

Revision ID: 73d62fcb29ef
Revises: f08c51acc35c
Create Date: 2025-04-07 23:47:37.531800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '73d62fcb29ef'
down_revision: Union[str, None] = 'f08c51acc35c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('admin', 'user', 'designer', name='userrole'),
               nullable=True)
    op.drop_column('users', 'disabled')
    op.drop_column('users', 'google_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('google_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('disabled', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('admin', 'user', 'designer', name='userrole'),
               nullable=False)
    # ### end Alembic commands ###
