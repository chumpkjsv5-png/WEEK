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


class Login:
    def __init__(
        self,
        users: UserAuthRepository,
        hasher: PasswordVerifier,
        tokens: TokenService,
    ):
        self.users = users
        self.hasher = hasher
        self.tokens = tokens

    def execute(self, email: str, password: str) -> str:
        email = email.strip().lower()
        creds = self.users.find_credentials_by_email(email)

        # Cùng một thông báo cho sai email và sai mật khẩu
        if creds is None or not self.hasher.verify(password, creds.password_hash):
            raise InvalidCredentials("Email hoặc mật khẩu không đúng")
        # Kiểm tra mật khẩu trước, is_active sau
        if not creds.is_active:
            raise AccountDisabled("Tài khoản đã bị vô hiệu hoá")
        return self.tokens.issue(str(creds.id))


class AuthenticateToken:
    def __init__(self, users: UserAuthRepository, tokens: TokenService):
        self.users = users
        self.tokens = tokens

    def execute(self, token: Optional[str]) -> AuthUser:
        if token is None:
            raise NotAuthenticated("Bạn chưa đăng nhập")

        user_id = self.tokens.verify(token)  # ném InvalidSession nếu không hợp lệ

        # Role và is_active luôn đọc từ DB, không lấy từ token
        user = self.users.get_auth_user(user_id)
        if user is None or not user.is_active:
            raise InvalidSession("Phiên đăng nhập không hợp lệ hoặc đã hết hạn")
        return user
