
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import exists, select, update
from sqlalchemy.orm import Session

from app.application.ports.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.refresh_session import NewRefreshSession, RefreshSession
from app.models.refresh_token import RefreshToken as RefreshTokenRow


class PostgresRefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(row: RefreshTokenRow) -> RefreshSession:
        return RefreshSession(
            id=row.id,
            user_id=row.user_id,
            family_id=row.family_id,
            token_hash=row.token_hash,
            expires_at=row.expires_at,
            created_at=row.created_at,
            revoked_at=row.revoked_at,
            replaced_by=row.replaced_by,
        )

    def add(self, new: NewRefreshSession) -> RefreshSession:
        row = RefreshTokenRow(
            user_id=new.user_id,
            family_id=new.family_id,
            token_hash=new.token_hash,
            expires_at=new.expires_at,
        )
        self.db.add(row)
        self.db.flush()
        self.db.refresh(row)
        return self._to_domain(row)

    def get_by_token_hash(
        self, token_hash: str
    ) -> Optional[RefreshSession]:
        row = self.db.scalar(
            select(RefreshTokenRow).where(
                RefreshTokenRow.token_hash == token_hash
            )
        )
        return self._to_domain(row) if row else None

    def consume(
        self,
        session_id: UUID,
        replaced_by: UUID,
        now: datetime,
    ) -> bool:
        result = self.db.execute(
            update(RefreshTokenRow)
            .where(
                RefreshTokenRow.id == session_id,
                RefreshTokenRow.revoked_at.is_(None),
                RefreshTokenRow.replaced_by.is_(None),
                RefreshTokenRow.expires_at > now,
            )
            .values(
                revoked_at=now,
                replaced_by=replaced_by,
            )
        )
        return result.rowcount == 1

    def revoke_family(self, family_id: UUID, now: datetime) -> None:
        self.db.execute(
            update(RefreshTokenRow)
            .where(
                RefreshTokenRow.family_id == family_id,
                RefreshTokenRow.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

    def revoke_all_for_user(self, user_id: UUID, now: datetime) -> None:
        self.db.execute(
            update(RefreshTokenRow)
            .where(
                RefreshTokenRow.user_id == user_id,
                RefreshTokenRow.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

    def is_family_active(self, family_id: UUID, now: datetime) -> bool:
        query = select(
            exists().where(
                RefreshTokenRow.family_id == family_id,
                RefreshTokenRow.revoked_at.is_(None),
                RefreshTokenRow.expires_at > now,
            )
        )
        return bool(self.db.scalar(query))
