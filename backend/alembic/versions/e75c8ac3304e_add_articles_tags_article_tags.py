"""add articles tags article_tags

Revision ID: e75c8ac3304e
Revises: f1c43e9d3b14
Create Date: 2026-10-21 10:48:30.589951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e75c8ac3304e'
down_revision: Union[str, Sequence[str], None] = 'f1c43e9d3b14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(220), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "status IN ('pending', 'published', 'failed')", name="ck_articles_status"
        ),
    )
    op.create_index("ix_articles_owner_id", "articles", ["owner_id"])
    op.create_index(
        "ix_articles_status_created", "articles", ["status", "created_at", "id"]
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.CheckConstraint("name = lower(btrim(name))", name="ck_tags_name_normalized"),
    )

    op.create_table(
        "article_tags",
        sa.Column(
            "article_id",
            sa.Integer,
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "tag_id",
            sa.Integer,
            sa.ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_index("ix_article_tags_tag_id", "article_tags", ["tag_id"])


def downgrade():
    op.drop_table("article_tags")
    op.drop_table("tags")
    op.drop_table("articles")
