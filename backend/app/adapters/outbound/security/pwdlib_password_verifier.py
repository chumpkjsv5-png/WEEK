from app.core.security import verify_password


class PwdlibPasswordVerifier:
    def verify(self, password: str, hashed: str) -> bool:
        return verify_password(password, hashed)