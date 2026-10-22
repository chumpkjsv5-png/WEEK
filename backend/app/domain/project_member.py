from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class MemberUser:
    id: UUID
    full_name: str
    email: str


@dataclass
class Member:
    project_id: int
    user_id: UUID
    created_at: Optional[datetime]
    user: MemberUser