from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Table, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_article_tags_tag_id", "tag_id"),
)


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        CheckConstraint("status IN ('pending','published','failed')", name="ck_articles_status"),
        Index("ix_articles_status_created", "status", "created_at", "id"),
    )

    id = Column(Integer, primary_key=True)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    slug = Column(String(220), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="pending", server_default="pending")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        CheckConstraint("name = lower(btrim(name))", name="ck_tags_name_normalized"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    articles = relationship("Article", secondary=article_tags, back_populates="tags")