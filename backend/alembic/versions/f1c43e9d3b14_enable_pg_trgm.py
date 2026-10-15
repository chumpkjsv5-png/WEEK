"""enable pg_trgm

Revision ID: f1c43e9d3b14
Revises: 02ac858ae07d
Create Date: 2026-10-15 11:26:11.750909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1c43e9d3b14'
down_revision: Union[str, Sequence[str], None] = '02ac858ae07d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
