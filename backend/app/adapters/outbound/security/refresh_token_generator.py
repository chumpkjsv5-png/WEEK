import hashlib
import secrets


class SecureRefreshTokenGenerator:
    """Generate a random refresh token and a hashed token to store in the database."""

    def new_token(self) -> str:
        return secrets.token_urlsafe(48)

    def hash_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()