import uuid
from typing import Protocol, Optional

class PasswordVerifier(Protocol):
    def verify(self, password: str, hashed: str) -> bool: ...


class TokenService(Protocol):
    def issue(
        self,
        user_id: str,
        session_id: Optional[str] = None,
    ) -> str: ...

    def verify(self, token: str) -> uuid.UUID:
        """Authenticate the JWT and return the user ID."""

    def get_session_id(self, token: str) -> Optional[uuid.UUID]:
        """Read the 'sid' from the JWT; returns None if the token does not contain a 'sid'."""