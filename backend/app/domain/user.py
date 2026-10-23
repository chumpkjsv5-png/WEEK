import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UserSummary:
    """Thông tin tối thiểu để chọn người (không có role, password)."""
    id: uuid.UUID
    full_name: str
    email: str