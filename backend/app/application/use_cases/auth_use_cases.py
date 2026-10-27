from typing import Optional

from app.application.ports.security import PasswordVerifier, TokenService
from app.application.ports.user_auth_repository import UserAuthRepository
from app.domain.auth import AuthUser
from app.domain.errors import (
    AccountDisabled,
    InvalidCredentials,
    InvalidSession,
    NotAuthenticated,
)
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.application.ports.refresh_token_generator import (
    RefreshTokenGenerator,
)
from app.application.ports.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.refresh_session import NewRefreshSession
from app.domain.token_pair import TokenPair


class Login:
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    def __init__(
        self,
        users: UserAuthRepository,
        hasher: PasswordVerifier,
        tokens: TokenService,
        refresh_tokens: RefreshTokenRepository,
        refresh_token_generator: RefreshTokenGenerator,
    ):
        self.users = users
        self.hasher = hasher
        self.tokens = tokens
        self.refresh_tokens = refresh_tokens
        self.refresh_token_generator = refresh_token_generator

    def execute(self, email: str, password: str) -> TokenPair:
        email = email.strip().lower()
        creds = self.users.find_credentials_by_email(email)

        if creds is None or not self.hasher.verify(
            password, creds.password_hash
        ):
            raise InvalidCredentials("Email hoặc mật khẩu không đúng")

        if not creds.is_active:
            raise AccountDisabled("Tài khoản đã bị vô hiệu hoá")

        now = datetime.now(timezone.utc)
        family_id = uuid4()
        refresh_token = self.refresh_token_generator.new_token()

        session = self.refresh_tokens.add(
            NewRefreshSession(
                user_id=creds.id,
                family_id=family_id,
                token_hash=self.refresh_token_generator.hash_token(
                    refresh_token
                ),
                expires_at=now + timedelta(
                    days=self.REFRESH_TOKEN_EXPIRE_DAYS
                ),
            )
        )

        access_token = self.tokens.issue(
            str(creds.id),
            session_id=str(session.id),
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        )

class RefreshAccessToken:
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    def __init__(
        self,
        users: UserAuthRepository,
        tokens: TokenService,
        refresh_tokens: RefreshTokenRepository,
        refresh_token_generator: RefreshTokenGenerator,
    ):
        self.users = users
        self.tokens = tokens
        self.refresh_tokens = refresh_tokens
        self.refresh_token_generator = refresh_token_generator

    def execute(self, raw_refresh_token: str) -> TokenPair:
        if not raw_refresh_token or not raw_refresh_token.strip():
            raise InvalidSession("Refresh token không hợp lệ")

        now = datetime.now(timezone.utc)
        token_hash = self.refresh_token_generator.hash_token(
            raw_refresh_token
        )
        session = self.refresh_tokens.get_by_token_hash(token_hash)

        if session is None:
            raise InvalidSession(
                "Refresh token không hợp lệ hoặc đã hết hạn"
            )

        if (
            session.revoked_at is not None
            or session.replaced_by is not None
            or session.expires_at <= now
        ):
            raise InvalidSession(
                "Refresh token không hợp lệ hoặc đã hết hạn"
            )

        user = self.users.get_auth_user(session.user_id)

        if user is None or not user.is_active:
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )

        new_raw_token = self.refresh_token_generator.new_token()

        new_session = self.refresh_tokens.add(
            NewRefreshSession(
                user_id=session.user_id,
                family_id=session.family_id,
                token_hash=self.refresh_token_generator.hash_token(
                    new_raw_token
                ),
                expires_at=now + timedelta(
                    days=self.REFRESH_TOKEN_EXPIRE_DAYS
                ),
            )
        )

        consumed = self.refresh_tokens.consume(
            session_id=session.id,
            replaced_by=new_session.id,
            now=now,
        )

        if not consumed:
            raise InvalidSession(
                "Refresh token không hợp lệ hoặc đã hết hạn"
            )

        access_token = self.tokens.issue(
            str(user.id),
            session_id=str(new_session.id),
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=new_raw_token,
        )



class AuthenticateToken:
    def __init__(
        self,
        users: UserAuthRepository,
        tokens: TokenService,
        refresh_tokens: RefreshTokenRepository,
    ):
        self.users = users
        self.tokens = tokens
        self.refresh_tokens = refresh_tokens

    def execute(self, token: Optional[str]) -> AuthUser:
        if token is None:
            raise NotAuthenticated("Bạn chưa đăng nhập")

        user_id = self.tokens.verify(token)
        session_id = self.tokens.get_session_id(token)

        if session_id is None:
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )

        session = self.refresh_tokens.get_by_id(session_id)
        now = datetime.now(timezone.utc)

        if (
            session is None
            or session.user_id != user_id
            or session.revoked_at is not None
            or session.replaced_by is not None
            or session.expires_at <= now
        ):
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )

        user = self.users.get_auth_user(user_id)

        if user is None or not user.is_active:
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )

        return user



# The 'role' and 'is_active' fields are always read from the database, not from the token.
        user = self.users.get_auth_user(user_id)
        if user is None or not user.is_active:
            raise InvalidSession("Phiên đăng nhập không hợp lệ hoặc đã hết hạn")
        return user
