import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthUser:
    """Người dùng đã xác thực. Router đọc id và role, nên giữ đủ các thuộc tính này."""
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool


@dataclass(frozen=True)
class UserCredentials:
    id: uuid.UUID
    password_hash: str
    is_active: bool
