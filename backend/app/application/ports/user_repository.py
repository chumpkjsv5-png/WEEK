import uuid
from typing import Optional, Protocol

from app.domain.user import UserSummary


class UserRepository(Protocol):
    def search_active(
        self, search: Optional[str], limit: int
    ) -> tuple[list[UserSummary], int]: ...

    def get(self, user_id: uuid.UUID) -> Optional[UserSummary]: ...