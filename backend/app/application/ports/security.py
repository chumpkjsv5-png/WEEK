import uuid
from typing import Protocol


class PasswordVerifier(Protocol):
    def verify(self, password: str, hashed: str) -> bool: ...


class TokenService(Protocol):
    def issue(self, user_id: str) -> str: ...

    def verify(self, token: str) -> uuid.UUID:
        """Ném InvalidSession nếu token sai, hết hạn hoặc thiếu sub hợp lệ."""