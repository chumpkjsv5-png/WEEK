# backend/app/application/use_cases/refresh_token.py
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional
from uuid import UUID, uuid4

from app.application.ports.refresh_token_generator import RefreshTokenGenerator
from app.application.ports.refresh_token_repository import RefreshTokenRepository

from app.application.ports.security import TokenService
from app.application.ports.user_repository import UserRepository

from app.domain.errors import RefreshTokenInvalid, RefreshTokenReused
from app.domain.refresh_session import NewRefreshSession, RefreshSession


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IssueRefreshToken:
    """Create a new refresh session. Login calls this to start a new token family (family_id=None), 
while RefreshAccessToken calls it to rotate tokens within the same family."""

    def __init__(
        self,
        sessions: RefreshTokenRepository,
        generator: RefreshTokenGenerator,
        ttl: timedelta,
        clock: Callable[[], datetime] = _utcnow,
    ):
        self.sessions = sessions
        self.generator = generator
        self.ttl = ttl
        self.clock = clock

    def execute(
        self, user_id: UUID, family_id: Optional[UUID] = None
    ) -> tuple[RefreshSession, str]:
        raw_token = self.generator.new_token()
        session = self.sessions.add(
            NewRefreshSession(
                user_id=user_id,
                family_id=family_id or uuid4(),
                token_hash=self.generator.hash_token(raw_token),
                expires_at=self.clock() + self.ttl,
            )
        )
        return session, raw_token  # raw_token chỉ trả cho client một lần


class RefreshAccessToken:
    def __init__(
        self,
        sessions: RefreshTokenRepository,
        users: UserRepository,
        tokens: TokenService,
        generator: RefreshTokenGenerator,
        issue: IssueRefreshToken,
        clock: Callable[[], datetime] = _utcnow,
    ):
        self.sessions = sessions
        self.users = users
        self.tokens = tokens
        self.generator = generator
        self.issue = issue
        self.clock = clock

    def execute(self, raw_token: str) -> tuple[str, str]:
        Return (access_token, new_refresh_token).
        now = self.clock()
        session = self.sessions.get_by_token_hash(
            self.generator.hash_token(raw_token)
        )
        if session is None:
            raise RefreshTokenInvalid("Refresh token không hợp lệ")

        # Đã xoay vòng mà vẫn bị mang đi dùng: nghi bị lộ, thu hồi cả họ
        if session.replaced_by is not None:
            self.sessions.revoke_family(session.family_id, now)
            raise RefreshTokenReused(
                "Phát hiện refresh token bị dùng lại, vui lòng đăng nhập lại"
            )

        # Đã bị thu hồi (logout) hoặc hết hạn
        if session.revoked_at is not None or session.expires_at <= now:
            raise RefreshTokenInvalid("Refresh token đã hết hạn hoặc bị thu hồi")

        # Tài khoản bị khóa hoặc bị xóa thì không cấp token mới
        user = self.users.get(session.user_id)
        if user is None or not user.is_active:
            self.sessions.revoke_family(session.family_id, now)
            raise RefreshTokenInvalid("Tài khoản không còn hiệu lực")

        new_session, new_raw = self.issue.execute(
            user.id, family_id=session.family_id
        )

        # Nguyên tử: hai request song song cùng token thì chỉ một request thắng
        if not self.sessions.consume(session.id, new_session.id, now):
            self.sessions.revoke_family(session.family_id, now)
            raise RefreshTokenReused(
                "Phát hiện refresh token bị dùng lại, vui lòng đăng nhập lại"
            )

        access_token = self.tokens.create_access_token(
            user.id, session_id=session.family_id
        )
        return access_token, new_raw


class LogoutSession:
"""Log out the current device by revoking the entire token family associated with sid."""

    def __init__(
        self,
        sessions: RefreshTokenRepository,
        clock: Callable[[], datetime] = _utcnow,
    ):
        self.sessions = sessions
        self.clock = clock

    def execute(self, session_id: UUID) -> None:
        self.sessions.revoke_family(session_id, self.clock())


class LogoutAllSessions:
    """Log out the user from all devices."""

    def __init__(
        self,
        sessions: RefreshTokenRepository,
        clock: Callable[[], datetime] = _utcnow,
    ):
        self.sessions = sessions
        self.clock = clock

    def execute(self, user_id: UUID) -> None:
        self.sessions.revoke_all_for_user(user_id, self.clock())