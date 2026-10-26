# backend/app/domain/refresh_session.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class RefreshSession:
    id: UUID
    user_id: UUID
    family_id: UUID  # cũng là `sid` trong access token
    token_hash: str
    expires_at: datetime
    created_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    replaced_by: Optional[UUID] = None


@dataclass(frozen=True)
class NewRefreshSession:
    user_id: UUID
    family_id: UUID
    token_hash: str
    expires_at: datetime