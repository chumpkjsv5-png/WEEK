from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.models.user_data import User


def authenticate(db: Session, email: str, password: str) -> User:
    email = email.strip().lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))

    # Cùng một thông báo cho sai email và sai mật khẩu
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError(
            "Email hoặc mật khẩu không đúng",
            code="INVALID_CREDENTIALS",
        )
    if not user.is_active:
        raise ForbiddenError(
            "Tài khoản đã bị vô hiệu hoá",
            code="ACCOUNT_DISABLED",
        )
    return user


def login(db: Session, email: str, password: str) -> str:
    user = authenticate(db, email, password)
    return create_access_token(str(user.id))