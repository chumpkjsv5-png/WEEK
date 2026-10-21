import logging
import re
import unicodedata
import uuid
from typing import Optional

from pymongo.collection import Collection
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    ContentMissingError,
    NotFoundError,
    StoreUnavailableError,
)
from app.models.article_data import Article, Tag
from app.models.user_data import User
from app.schemas.article_schema import ArticleCreate
from app.services import article_content_service as content_service

logger = logging.getLogger(__name__)

DEFAULT_ARTICLE_LIMIT = 10
MAX_ARTICLE_LIMIT = 50


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _make_slug(title: str) -> str:
    text = title.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:150] or "bai-viet"
    return f"{text}-{uuid.uuid4().hex[:6]}"


def _get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    if not names:
        return []
    db.execute(
        pg_insert(Tag)
        .values([{"name": n} for n in names])
        .on_conflict_do_nothing(index_elements=["name"])
    )
    return list(db.scalars(select(Tag).where(Tag.name.in_(names))).all())


def _set_status(db: Session, article_id: int, status: str) -> None:
    db.rollback()
    article = db.get(Article, article_id)
    article.status = status
    db.commit()


def create_article(
    db: Session, content: Collection, owner: User, data: ArticleCreate
) -> Article:
    # Bước 1: SQL là nguồn sự thật, commit "pending" trước khi đụng Mongo
    article = Article(
        owner_id=owner.id,
        title=data.title,
        slug=_make_slug(data.title),
        status="pending",
        tags=_get_or_create_tags(db, data.tags),
    )
    db.add(article)
    db.commit()
    article_id = article.id

    # Bước 2: ghi nội dung vào Mongo
    try:
        content_service.insert_content(
            content, article_id, [b.model_dump() for b in data.blocks]
        )
    except Exception:
        logger.exception("Mongo insert failed, article_id=%s", article_id)
        try:
            _set_status(db, article_id, "failed")
        except Exception:
            logger.exception("Không đánh dấu được failed, article_id=%s", article_id)
        raise StoreUnavailableError("Không lưu được nội dung bài viết")

    # Bước 3: xác nhận published; nếu lỗi thì bù trừ bằng cách xóa nội dung Mongo
    try:
        _set_status(db, article_id, "published")
    except Exception:
        logger.exception("SQL publish failed, article_id=%s", article_id)
        try:
            content_service.delete_content(content, article_id)
        except Exception:
            logger.exception("Bù trừ lỗi, cần đối soát, article_id=%s", article_id)
        raise StoreUnavailableError("Không hoàn tất được bài viết")

    return db.scalar(
        select(Article).options(selectinload(Article.tags)).where(Article.id == article_id)
    )


def get_article(db: Session, content: Collection, article_id: int) -> dict:
    article = db.scalar(
        select(Article)
        .options(selectinload(Article.tags))
        .where(Article.id == article_id, Article.status == "published")
    )
    if not article:
        raise NotFoundError("Bài viết không tồn tại", code="ARTICLE_NOT_FOUND")

    try:
        blocks = content_service.get_content(content, article_id)
    except Exception:
        logger.exception("Mongo read failed, article_id=%s", article_id)
        raise StoreUnavailableError("Không đọc được nội dung bài viết")

    if blocks is None:
        logger.error("CONTENT_MISSING: article_id=%s có ở SQL nhưng thiếu ở Mongo", article_id)
        raise ContentMissingError("Bài viết tồn tại nhưng nội dung bị thiếu")

    return {"article": article, "blocks": blocks}


def search_articles(
    db: Session,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = DEFAULT_ARTICLE_LIMIT,
    offset: int = 0,
) -> dict:
    limit = min(max(limit, 1), MAX_ARTICLE_LIMIT)
    offset = max(offset, 0)

    filters = [Article.status == "published"]
    if tag and tag.strip():
        filters.append(Article.tags.any(Tag.name == tag.strip().lower()))
    if q and q.strip():
        contains = f"%{_escape_like(q.strip())}%"
        filters.append(
            func.unaccent(Article.title).ilike(func.unaccent(contains), escape="\\")
        )

    total = db.scalar(select(func.count()).select_from(Article).where(*filters)) or 0
    items = db.scalars(
        select(Article)
        .options(selectinload(Article.tags))
        .where(*filters)
        .order_by(Article.created_at.desc(), Article.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return {"items": items, "total": total}