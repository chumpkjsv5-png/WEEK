import uuid
from typing import Optional

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.domain.user import UserSummary
from app.models.user_data import User as UserRow

SIMILARITY_THRESHOLD = 0.3


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _to_domain(row: UserRow) -> UserSummary:
    return UserSummary(id=row.id, full_name=row.full_name, email=row.email)


class PostgresUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_active(
        self, search: Optional[str], limit: int
    ) -> tuple[list[UserSummary], int]:
        filters = [UserRow.is_active.is_(True)]
        order = [UserRow.full_name.asc()]

        if search and search.strip():
            term = search.strip()
            contains = f"%{_escape_like(term)}%"
            prefix = f"{_escape_like(term)}%"

            name = func.unaccent(UserRow.full_name)
            mail = func.unaccent(UserRow.email)
            q = func.unaccent(term)

            filters.append(
                or_(
                    name.ilike(func.unaccent(contains), escape="\\"),
                    mail.ilike(func.unaccent(contains), escape="\\"),
                    func.similarity(name, q) > SIMILARITY_THRESHOLD,
                )
            )
            order = [
                # tên bắt đầu bằng từ khoá > tên chứa từ khoá > chỉ gần giống
                case(
                    (name.ilike(func.unaccent(prefix), escape="\\"), 0),
                    (name.ilike(func.unaccent(contains), escape="\\"), 1),
                    else_=2,
                ),
                func.similarity(name, q).desc(),
                UserRow.full_name.asc(),
            ]

        total = self.db.scalar(
            select(func.count()).select_from(UserRow).where(*filters)
        ) or 0
        rows = self.db.scalars(
            select(UserRow).where(*filters).order_by(*order).limit(limit)
        ).all()
        return [_to_domain(r) for r in rows], total

    def get(self, user_id: uuid.UUID) -> Optional[UserSummary]:
        row = self.db.get(UserRow, user_id)
        return _to_domain(row) if row else None
