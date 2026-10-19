import uuid
from typing import Optional

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.user_data import User

DEFAULT_USER_LIMIT = 5
MAX_USER_LIMIT = 50
SIMILARITY_THRESHOLD = 0.3


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_users(
    db: Session,
    search: Optional[str] = None,
    limit: int = DEFAULT_USER_LIMIT,
) -> dict:
    limit = min(max(limit, 1), MAX_USER_LIMIT)

    filters = [User.is_active.is_(True)]
    order = [User.full_name.asc()]

    if search and search.strip():
        term = search.strip()
        contains = f"%{_escape_like(term)}%"
        prefix = f"{_escape_like(term)}%"

        name = func.unaccent(User.full_name)
        mail = func.unaccent(User.email)
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
            User.full_name.asc(),
        ]

    total = db.scalar(select(func.count()).select_from(User).where(*filters)) or 0
    items = db.scalars(
        select(User).where(*filters).order_by(*order).limit(limit)
    ).all()
    return {"items": items, "total": total}


def get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError("User không tồn tại", code="USER_NOT_FOUND")
    return user