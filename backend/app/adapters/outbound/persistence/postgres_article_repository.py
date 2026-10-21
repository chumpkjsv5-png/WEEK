import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, selectinload

from app.domain.article import Article, ArticleStatus
from app.models.article_data import Article as ArticleRow
from app.models.article_data import Tag


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _to_domain(row: ArticleRow) -> Article:
    return Article(
        id=row.id,
        owner_id=row.owner_id,
        title=row.title,
        slug=row.slug,
        status=row.status,
        tags=sorted(t.name for t in row.tags),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_tags(self, names: list[str]) -> list[Tag]:
        if not names:
            return []
        self.db.execute(
            pg_insert(Tag)
            .values([{"name": n} for n in names])
            .on_conflict_do_nothing(index_elements=["name"])
        )
        return list(self.db.scalars(select(Tag).where(Tag.name.in_(names))).all())

    def create_pending(
        self, owner_id: uuid.UUID, title: str, slug: str, tags: list[str]
    ) -> int:
        row = ArticleRow(
            owner_id=owner_id,
            title=title,
            slug=slug,
            status=ArticleStatus.PENDING,
            tags=self._get_or_create_tags(tags),
        )
        self.db.add(row)
        self.db.commit()  # pending phải nằm chắc trong SQL trước khi ghi Mongo
        return row.id

    def set_status(self, article_id: int, status: str) -> None:
        self.db.rollback()  # dọn session nếu đang ở trạng thái lỗi
        row = self.db.get(ArticleRow, article_id)
        row.status = status
        self.db.commit()

    def get(self, article_id: int) -> Optional[Article]:
        row = self.db.scalar(
            select(ArticleRow)
            .options(selectinload(ArticleRow.tags))
            .where(ArticleRow.id == article_id)
        )
        return _to_domain(row) if row else None

    def search(
        self, q: Optional[str], tag: Optional[str], limit: int, offset: int
    ) -> tuple[list[Article], int]:
        filters = [ArticleRow.status == ArticleStatus.PUBLISHED]
        if tag and tag.strip():
            filters.append(ArticleRow.tags.any(Tag.name == tag.strip().lower()))
        if q and q.strip():
            contains = f"%{_escape_like(q.strip())}%"
            filters.append(
                func.unaccent(ArticleRow.title).ilike(func.unaccent(contains), escape="\\")
            )

        total = self.db.scalar(
            select(func.count()).select_from(ArticleRow).where(*filters)
        ) or 0
        rows = self.db.scalars(
            select(ArticleRow)
            .options(selectinload(ArticleRow.tags))
            .where(*filters)
            .order_by(ArticleRow.created_at.desc(), ArticleRow.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
        return [_to_domain(r) for r in rows], total