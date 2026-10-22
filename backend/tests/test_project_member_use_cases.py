import uuid

import pytest

from app.application.use_cases.project_member_use_cases import (
    AddMember,
    ListMembers,
    RemoveMember,
    SearchUsersToAdd,
)
from app.domain.errors import (
    CannotRemoveOwner,
    MemberAlreadyExists,
    MemberHasOpenTasks,
    MemberNotFound,
    ProjectMemberForbidden,
    ProjectNotFound,
    UserNotFound,
)
from app.domain.project import Project, ProjectActor
from app.domain.project_member import Member, MemberUser


class FakeRepo:
    def __init__(self, owner_id, users=()):
        self.owner_id = owner_id
        self.users = {u: MemberUser(u, f"User {u}", f"{u}@x.com") for u in users}
        self.members = {owner_id}
        self.open_tasks = {}
        self.search_called = False

    def get_project(self, project_id):
        if project_id != 1:
            return None
        return Project(1, "A", None, self.owner_id)

    def list_members(self, project_id):
        return [Member(1, u, None, self.users[u]) for u in self.members if u in self.users]

    def search_candidates(self, project_id, q, limit):
        self.search_called = True
        return [u for uid, u in self.users.items() if uid not in self.members][:limit]

    def user_exists(self, user_id):
        return user_id in self.users

    def get_member(self, project_id, user_id):
        if user_id in self.members:
            return Member(1, user_id, None, self.users[user_id])
        return None

    def add(self, project_id, user_id):
        self.members.add(user_id)
        return Member(1, user_id, None, self.users[user_id])

    def remove(self, project_id, user_id):
        self.members.discard(user_id)

    def count_open_tasks(self, project_id, user_id):
        return self.open_tasks.get(user_id, 0)


def _setup():
    owner, other = uuid.uuid4(), uuid.uuid4()
    repo = FakeRepo(owner, users={owner, other})
    actor = ProjectActor(owner, is_admin=False, is_manager=True)
    return repo, owner, other, actor


def test_manager_owner_can_add_member():
    repo, owner, other, actor = _setup()
    AddMember(repo).execute(1, other, actor)
    assert other in repo.members


def test_other_manager_cannot_add_member():
    repo, owner, other, actor = _setup()
    stranger = ProjectActor(uuid.uuid4(), is_admin=False, is_manager=True)
    with pytest.raises(ProjectMemberForbidden):
        AddMember(repo).execute(1, other, stranger)


def test_admin_can_manage_any_project():
    repo, owner, other, actor = _setup()
    admin = ProjectActor(uuid.uuid4(), is_admin=True, is_manager=False)
    AddMember(repo).execute(1, other, admin)
    assert other in repo.members


def test_add_unknown_user_raises_not_found():
    repo, owner, other, actor = _setup()
    with pytest.raises(UserNotFound):
        AddMember(repo).execute(1, uuid.uuid4(), actor)


def test_add_duplicate_member_raises_conflict():
    repo, owner, other, actor = _setup()
    with pytest.raises(MemberAlreadyExists):
        AddMember(repo).execute(1, owner, actor)


def test_cannot_remove_owner():
    repo, owner, other, actor = _setup()
    with pytest.raises(CannotRemoveOwner):
        RemoveMember(repo).execute(1, owner, actor)


def test_remove_non_member_raises_not_found():
    repo, owner, other, actor = _setup()
    with pytest.raises(MemberNotFound):
        RemoveMember(repo).execute(1, other, actor)


def test_cannot_remove_member_with_open_tasks():
    repo, owner, other, actor = _setup()
    AddMember(repo).execute(1, other, actor)
    repo.open_tasks[other] = 2
    with pytest.raises(MemberHasOpenTasks, match="2 task"):
        RemoveMember(repo).execute(1, other, actor)
    assert other in repo.members


def test_remove_member_without_open_tasks():
    repo, owner, other, actor = _setup()
    AddMember(repo).execute(1, other, actor)
    RemoveMember(repo).execute(1, other, actor)
    assert other not in repo.members


def test_search_with_blank_query_returns_empty_without_hitting_repo():
    repo, owner, other, actor = _setup()
    assert SearchUsersToAdd(repo).execute(1, "   ", actor) == []
    assert repo.search_called is False


def test_unknown_project_raises_not_found():
    repo, owner, other, actor = _setup()
    with pytest.raises(ProjectNotFound):
        ListMembers(repo).execute(999)