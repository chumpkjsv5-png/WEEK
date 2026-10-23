import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.auth import AuthUser, UserCredentials
from app.models.user_data import User as UserRow


class PostgresUserAuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_credentials_by_email(self, email: str) -> Optional[UserCredentials]:
        row = self.db.scalar(select(UserRow).where(func.lower(UserRow.email) == email))
        if row is None:
            return None
        return UserCredentials(
            id=row.id, password_hash=row.password_hash, is_active=row.is_active
        )

    def get_auth_user(self, user_id: uuid.UUID) -> Optional[AuthUser]:
        row = self.db.get(UserRow, user_id)
        if row is None:
            return None
        return AuthUser(
            id=row.id,
            email=row.email,
            full_name=row.full_name,
            role=row.role,
            is_active=row.is_active,
        )
