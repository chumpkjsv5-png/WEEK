
import uuid

import jwt

from app.core.security import create_access_token, decode_access_token
from app.domain.errors import InvalidSession


class JwtTokenService:
    def issue(
        self,
        user_id: str,
          session_id: str | None = None,
    ) -> str:
        return create_access_token(user_id, session_id)

    def verify(self, token: str) -> uuid.UUID:
        try:
            payload = decode_access_token(token)
            return uuid.UUID(payload["sub"])
        except (jwt.PyJWTError, KeyError, ValueError):
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )

    def get_session_id(self, token: str) -> uuid.UUID | None:
        try:
            payload = decode_access_token(token)
            raw_session_id = payload.get("sid")

            if raw_session_id is None:
                return None

            return uuid.UUID(raw_session_id)
        except (jwt.PyJWTError, KeyError, ValueError, TypeError):
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )
