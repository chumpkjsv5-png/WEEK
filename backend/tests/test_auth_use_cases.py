import uuid

import pytest

from app.application.use_cases.auth_use_cases import AuthenticateToken, Login
from app.domain.auth import AuthUser, UserCredentials
from app.domain.errors import (
    AccountDisabled,
    InvalidCredentials,
    InvalidSession,
    NotAuthenticated,
)


class FakeAuthRepo:
    def __init__(self):
        self.creds = {}  # email -> UserCredentials
        self.users = {}  # id -> AuthUser

    def add(self, email, password, is_active=True, role="member"):
        uid = uuid.uuid4()
        self.creds[email] = UserCredentials(uid, f"hashed:{password}", is_active)
        self.users[uid] = AuthUser(uid, email, "Tên", role, is_active)
        return uid

    def find_credentials_by_email(self, email):
        return self.creds.get(email)

    def get_auth_user(self, user_id):
        return self.users.get(user_id)


class FakeHasher:
    def verify(self, password, hashed):
        return hashed == f"hashed:{password}"


class FakeTokens:
    def issue(self, user_id):
        return f"tok:{user_id}"

    def verify(self, token):
        if not token.startswith("tok:"):
            raise InvalidSession("Phiên đăng nhập không hợp lệ hoặc đã hết hạn")
        try:
            return uuid.UUID(token[4:])
        except ValueError:
            raise InvalidSession("Phiên đăng nhập không hợp lệ hoặc đã hết hạn")


def _login(repo):
    return Login(repo, FakeHasher(), FakeTokens())


def _auth(repo):
    return AuthenticateToken(repo, FakeTokens())


def test_login_success_returns_token_for_user():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")
    assert _login(repo).execute("a@x.com", "secret") == f"tok:{uid}"


def test_login_normalizes_email():
    repo = FakeAuthRepo()
    repo.add("a@x.com", "secret")
    assert _login(repo).execute("  A@X.COM ", "secret").startswith("tok:")


def test_wrong_password_and_unknown_email_share_the_same_error():
    repo = FakeAuthRepo()
    repo.add("a@x.com", "secret")
    with pytest.raises(InvalidCredentials) as wrong_pw:
        _login(repo).execute("a@x.com", "bad")
    with pytest.raises(InvalidCredentials) as no_user:
        _login(repo).execute("nobody@x.com", "secret")
    assert str(wrong_pw.value) == str(no_user.value)


def test_disabled_account_with_correct_password_is_rejected():
    repo = FakeAuthRepo()
    repo.add("a@x.com", "secret", is_active=False)
    with pytest.raises(AccountDisabled):
        _login(repo).execute("a@x.com", "secret")


def test_disabled_account_with_wrong_password_does_not_reveal_status():
    repo = FakeAuthRepo()
    repo.add("a@x.com", "secret", is_active=False)
    with pytest.raises(InvalidCredentials):
        _login(repo).execute("a@x.com", "bad")


def test_authenticate_without_token_raises_not_authenticated():
    with pytest.raises(NotAuthenticated):
        _auth(FakeAuthRepo()).execute(None)


def test_authenticate_with_garbage_token_raises_invalid_session():
    with pytest.raises(InvalidSession):
        _auth(FakeAuthRepo()).execute("rac-ruoi")


def test_authenticate_with_unknown_user_raises_invalid_session():
    with pytest.raises(InvalidSession):
        _auth(FakeAuthRepo()).execute(f"tok:{uuid.uuid4()}")


def test_authenticate_deactivated_user_raises_invalid_session():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")
    repo.users[uid] = AuthUser(uid, "a@x.com", "Tên", "member", False)
    with pytest.raises(InvalidSession):
        _auth(repo).execute(f"tok:{uid}")


def test_authenticate_reads_role_from_repository_not_from_token():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret", role="member")
    token = _login(repo).execute("a@x.com", "secret")
    repo.users[uid] = AuthUser(uid, "a@x.com", "Tên", "admin", True)  # đổi role sau khi cấp token
    assert _auth(repo).execute(token).role == "admin"
