import uuid
from typing import Optional

from app.application.ports.user_repository import UserRepository
from app.domain.errors import UserNotFound
from app.domain.user import UserSummary

DEFAULT_USER_LIMIT = 5
MAX_USER_LIMIT = 50


class SearchUsers:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(
        self, search: Optional[str] = None, limit: int = DEFAULT_USER_LIMIT
    ) -> dict:
        limit = min(max(limit, 1), MAX_USER_LIMIT)
        items, total = self.users.search_active(search, limit)
        return {"items": items, "total": total}


class GetUser:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(self, user_id: uuid.UUID) -> UserSummary:
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFound("User không tồn tại")
        return user
