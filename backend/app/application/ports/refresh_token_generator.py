# backend/app/application/ports/refresh_token_generator.py
from typing import Protocol
 
 
class RefreshTokenGenerator(Protocol):
    def new_token(self) -> str:
        """Generate a cryptographically secure random string, returned to the client only once."""

    def hash_token(self, raw_token: str) -> str:
        """Return the SHA-256 hash as a 64-character hexadecimal string for storage and lookup."""