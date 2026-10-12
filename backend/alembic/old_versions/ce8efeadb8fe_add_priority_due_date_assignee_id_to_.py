"""add priority due_date assignee_id to tasks

Revision ID: ce8efeadb8fe
Revises: 5bf6a0ec10c8
Create Date: 2026-10-09 14:48:01.841744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ce8efeadb8fe'
down_revision: Union[str, Sequence[str], None] = '5bf6a0ec10c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


priority_enum = postgresql.ENUM(
    'Low', 'Medium', 'High', name='priority_enum', create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Tạo enum type trước (cột cần nó)
    priority_enum.create(op.get_bind(), checkfirst=True)

    # 2. priority: NOT NULL + server_default => Postgres tự backfill 'Medium' cho dòng cũ
    op.add_column('tasks', sa.Column(
        'priority', priority_enum, server_default='Medium', nullable=False))

    # 3. due_date, assignee_id: nullable (task cũ = "chưa có")
    op.add_column('tasks', sa.Column('due_date', sa.Date(), nullable=True))
    op.add_column('tasks', sa.Column('assignee_id', sa.UUID(), nullable=True))

    # 4. Ràng buộc và index đặt sau cùng
    op.create_foreign_key(
        'tasks_assignee_id_fkey', 'tasks', 'users',
        ['assignee_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_tasks_assignee_id'), 'tasks', ['assignee_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Ngược thứ tự upgrade: index -> FK -> cột -> type
    op.drop_index(op.f('ix_tasks_assignee_id'), table_name='tasks')
    op.drop_constraint('tasks_assignee_id_fkey', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'assignee_id')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'priority')
    priority_enum.drop(op.get_bind(), checkfirst=True)