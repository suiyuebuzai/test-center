"""seed_roles

Revision ID: a1b2c3d4e5f6
Revises: 0347343374b3
Create Date: 2026-06-09 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '0347343374b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(
        sa.table('roles',
            sa.column('id', sa.SmallInteger),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
        ),
        [
            {'id': 1, 'name': 'admin',  'description': '管理员'},
            {'id': 2, 'name': 'tester', 'description': '测试人员'},
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE id IN (1, 2)")
