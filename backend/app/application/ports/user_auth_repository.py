import uuid
from typing import Optional, Protocol

from app.domain.auth import AuthUser, UserCredentials


class UserAuthRepository(Protocol):
    def find_credentials_by_email(self, email: str) -> Optional[UserCredentials]:
        """So khớp email không phân biệt hoa thường. Email đã được chuẩn hóa."""

    def get_auth_user(self, user_id: uuid.UUID) -> Optional[AuthUser]: ...