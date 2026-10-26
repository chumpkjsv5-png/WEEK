import uuid

import pytest

from app.application.use_cases.user_use_cases import GetUser, SearchUsers
from app.domain.errors import UserNotFound
from app.domain.user import UserSummary


class FakeUserRepo:
    def __init__(self, users=()):
        self.users = {u.id: u for u in users}
        self.last_limit = None

    def search_active(self, search, limit):
        self.last_limit = limit
        items = list(self.users.values())
        return items[:limit], len(items)

    def get(self, user_id):
        return self.users.get(user_id)


def test_search_clamps_limit():
    repo = FakeUserRepo()
    SearchUsers(repo).execute(limit=10_000)
    assert repo.last_limit == 50
    SearchUsers(repo).execute(limit=-3)
    assert repo.last_limit == 1


def test_get_user_returns_summary():
    uid = uuid.uuid4()
    repo = FakeUserRepo([UserSummary(uid, "An", "an@x.com")])
    assert GetUser(repo).execute(uid).email == "an@x.com"


def test_get_unknown_user_raises_not_found():
    with pytest.raises(UserNotFound):
        GetUser(FakeUserRepo()).execute(uuid.uuid4())
