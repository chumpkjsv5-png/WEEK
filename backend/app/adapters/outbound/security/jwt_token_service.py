import uuid

import jwt

from app.core.security import create_access_token, decode_access_token
from app.domain.errors import InvalidSession


class JwtTokenService:
    def issue(self, user_id: str) -> str:
        return create_access_token(user_id)

    def verify(self, token: str) -> uuid.UUID:
        try:
            payload = decode_access_token(token)
            return uuid.UUID(payload["sub"])
        except (jwt.PyJWTError, KeyError, ValueError):
            raise InvalidSession("Phiên đăng nhập không hợp lệ hoặc đã hết hạn")