import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.application.use_cases.auth_use_cases import AuthenticateToken, Login
from app.domain.auth import AuthUser, UserCredentials
from app.domain.errors import (
    AccountDisabled,
    InvalidCredentials,
    InvalidSession,
    NotAuthenticated,
)
from app.domain.refresh_session import RefreshSession


class FakeAuthRepo:
    def __init__(self):
        self.creds = {}  # email -> UserCredentials
        self.users = {}  # id -> AuthUser

    def add(self, email, password, is_active=True, role="member"):
        uid = uuid.uuid4()

        self.creds[email] = UserCredentials(
            uid,
            f"hashed:{password}",
            is_active,
        )

        self.users[uid] = AuthUser(
            uid,
            email,
            "Tên",
            role,
            is_active,
        )

        return uid

    def find_credentials_by_email(self, email):
        return self.creds.get(email)

    def get_auth_user(self, user_id):
        return self.users.get(user_id)


class FakeHasher:
    def verify(self, password, hashed):
        return hashed == f"hashed:{password}"


class FakeTokens:
    def __init__(self):
        self.session_ids = {}

    def issue(self, user_id, session_id=None):
        token = f"tok:{user_id}"

        self.session_ids[token] = (
            uuid.UUID(str(session_id))
            if session_id is not None
            else None
        )

        return token

    def verify(self, token):
        if not token.startswith("tok:"):
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )

        try:
            return uuid.UUID(token[4:])
        except ValueError:
            raise InvalidSession(
                "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            )

    def get_session_id(self, token):
        return self.session_ids.get(token)


class FakeRefreshTokenRepo:
    def __init__(self):
        self.sessions = []

    def add(self, new):
        session = RefreshSession(
            id=uuid.uuid4(),
            user_id=new.user_id,
            family_id=new.family_id,
            token_hash=new.token_hash,
            expires_at=new.expires_at,
        )

        self.sessions.append(session)
        return session

    def get_by_id(self, session_id):
        return next(
            (
                session
                for session in self.sessions
                if session.id == session_id
            ),
            None,
        )


class FakeRefreshTokenGenerator:
    def new_token(self):
        return "fake-refresh-token"

    def hash_token(self, raw_token):
        return f"hash:{raw_token}"


def _login(repo):
    return Login(
        repo,
        FakeHasher(),
        FakeTokens(),
        FakeRefreshTokenRepo(),
        FakeRefreshTokenGenerator(),
    )


def _auth(repo, refresh_tokens=None, tokens=None):
    return AuthenticateToken(
        repo,
        tokens or FakeTokens(),
        refresh_tokens or FakeRefreshTokenRepo(),
    )


def _add_active_session(repo, user_id, tokens, refresh_tokens):
    """Tạo session hợp lệ và access token tương ứng cho test."""
    now = datetime.now(timezone.utc)

    session = RefreshSession(
        id=uuid.uuid4(),
        user_id=user_id,
        family_id=uuid.uuid4(),
        token_hash="test-hash",
        expires_at=now + timedelta(days=7),
    )

    refresh_tokens.sessions.append(session)

    token = tokens.issue(
        str(user_id),
        session_id=str(session.id),
    )

    return token, session


def test_login_success_returns_access_and_refresh_tokens():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")

    result = _login(repo).execute("a@x.com", "secret")

    assert result.access_token == f"tok:{uid}"
    assert result.refresh_token == "fake-refresh-token"


def test_login_normalizes_email():
    repo = FakeAuthRepo()
    repo.add("a@x.com", "secret")

    result = _login(repo).execute("  A@X.COM ", "secret")

    assert result.access_token.startswith("tok:")
    assert result.refresh_token == "fake-refresh-token"


def test_login_persists_hashed_refresh_token():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")
    login = _login(repo)

    result = login.execute("a@x.com", "secret")

    assert len(login.refresh_tokens.sessions) == 1

    session = login.refresh_tokens.sessions[0]

    assert session.user_id == uid
    assert session.token_hash == "hash:fake-refresh-token"
    assert session.token_hash != result.refresh_token
    assert session.family_id is not None


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
    repo = FakeAuthRepo()
    tokens = FakeTokens()
    refresh_tokens = FakeRefreshTokenRepo()

    uid = uuid.uuid4()
    token, _ = _add_active_session(
        repo,
        uid,
        tokens,
        refresh_tokens,
    )

    with pytest.raises(InvalidSession):
        _auth(repo, refresh_tokens, tokens).execute(token)


def test_authenticate_deactivated_user_raises_invalid_session():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")

    repo.users[uid] = AuthUser(
        uid,
        "a@x.com",
        "Tên",
        "member",
        False,
    )

    tokens = FakeTokens()
    refresh_tokens = FakeRefreshTokenRepo()

    token, _ = _add_active_session(
        repo,
        uid,
        tokens,
        refresh_tokens,
    )

    with pytest.raises(InvalidSession):
        _auth(repo, refresh_tokens, tokens).execute(token)


def test_authenticate_reads_role_from_repository_not_from_token():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret", role="member")

    tokens = FakeTokens()
    refresh_tokens = FakeRefreshTokenRepo()

    token, _ = _add_active_session(
        repo,
        uid,
        tokens,
        refresh_tokens,
    )

    repo.users[uid] = AuthUser(
        uid,
        "a@x.com",
        "Tên",
        "admin",
        True,
    )

    result = _auth(repo, refresh_tokens, tokens).execute(token)

    assert result.role == "admin"


def test_authenticate_rejects_token_without_session_id():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")

    tokens = FakeTokens()
    token = tokens.issue(str(uid))

    with pytest.raises(InvalidSession):
        _auth(repo, FakeRefreshTokenRepo(), tokens).execute(token)


def test_authenticate_rejects_revoked_session():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")

    tokens = FakeTokens()
    refresh_tokens = FakeRefreshTokenRepo()

    token, session = _add_active_session(
        repo,
        uid,
        tokens,
        refresh_tokens,
    )

    session.revoked_at = datetime.now(timezone.utc)

    with pytest.raises(InvalidSession):
        _auth(repo, refresh_tokens, tokens).execute(token)


def test_authenticate_rejects_replaced_session():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")

    tokens = FakeTokens()
    refresh_tokens = FakeRefreshTokenRepo()

    token, session = _add_active_session(
        repo,
        uid,
        tokens,
        refresh_tokens,
    )

    session.replaced_by = uuid.uuid4()

    with pytest.raises(InvalidSession):
        _auth(repo, refresh_tokens, tokens).execute(token)


def test_authenticate_rejects_expired_session():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret")

    tokens = FakeTokens()
    refresh_tokens = FakeRefreshTokenRepo()

    token, session = _add_active_session(
        repo,
        uid,
        tokens,
        refresh_tokens,
    )

    session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    with pytest.raises(InvalidSession):
        _auth(repo, refresh_tokens, tokens).execute(token)


def test_authenticate_accepts_active_session():
    repo = FakeAuthRepo()
    uid = repo.add("a@x.com", "secret", role="member")

    tokens = FakeTokens()
    refresh_tokens = FakeRefreshTokenRepo()

    token, _ = _add_active_session(
        repo,
        uid,
        tokens,
        refresh_tokens,
    )

    result = _auth(repo, refresh_tokens, tokens).execute(token)

    assert result.id == uid
    assert result.role == "member"
