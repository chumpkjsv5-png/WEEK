# backend/app/application/ports/refresh_token_repository.py
from datetime import datetime
from typing import Optional, Protocol
from uuid import UUID

from app.domain.refresh_session import NewRefreshSession, RefreshSession


class RefreshTokenRepository(Protocol):
    def add(self, new: NewRefreshSession) -> RefreshSession: ...

    def get_by_token_hash(self, token_hash: str) -> Optional[RefreshSession]: ...

    def get_by_id(self, session_id: UUID) -> Optional[RefreshSession]: ...

    def consume(self, session_id: UUID, replaced_by: UUID, now: datetime) -> bool:
        """Only update the token if it has not been revoked. Return True if the update succeeds, 
        or False if another request has already used this token (treat it as token reuse)..
        """

    def revoke_family(self, family_id: UUID, now: datetime) -> None: ...

    def revoke_all_for_user(self, user_id: UUID, now: datetime) -> None: ...

    def is_family_active(self, family_id: UUID, now: datetime) -> bool:
        """The token family has at least one token that has not been revoked and has not expired."""