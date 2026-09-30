"""add priority to tasks

Revision ID: 3a08d747ad9e
Revises: 
Create Date: 2026-09-30 14:04:00.663949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3a08d747ad9e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


priority_enum = postgresql.ENUM(
    "Low", "Medium", "High",
    name="priority_enum",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'priority_enum') THEN
                CREATE TYPE priority_enum AS ENUM ('Low', 'Medium', 'High');
            END IF;
        END$$;
    """)

    op.add_column(
        "tasks",
        sa.Column(
            "priority",
            priority_enum,
            nullable=False,
            server_default="Medium",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tasks", "priority")
    op.execute("DROP TYPE IF EXISTS priority_enum")