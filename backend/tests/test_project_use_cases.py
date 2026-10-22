import uuid

import pytest

from app.application.use_cases.project_use_cases import (
    CreateProject,
    DeleteProject,
    GetProject,
    ListProjects,
    UpdateProject,
)
from app.domain.errors import (
    OwnerNotFound,
    ProjectForbidden,
    ProjectNotFound,
    ProjectOwnerChangeForbidden,
)
from app.domain.project import Project, ProjectActor, ProjectFilter


class FakeProjectRepo:
    def __init__(self, users=()):
        self.users = set(users)
        self.projects = {}
        self.members = set()
        self.last_filter = None

    def user_exists(self, user_id):
        return user_id in self.users

    def get(self, project_id):
        return self.projects.get(project_id)

    def add_with_owner_member(self, new):
        project = Project(len(self.projects) + 1, new.name, new.description, new.owner_id)
        self.projects[project.id] = project
        self.members.add((project.id, new.owner_id))
        return project

    def search(self, f):
        self.last_filter = f
        items = list(self.projects.values())
        return items[f.skip:f.skip + f.limit], len(items)

    def update(self, project_id, changes):
        project = self.projects[project_id]
        for key, value in changes.items():
            setattr(project, key, value)
        return project

    def delete(self, project_id):
        self.projects.pop(project_id, None)


def _manager(user_id=None):
    return ProjectActor(user_id or uuid.uuid4(), is_admin=False, is_manager=True)


def _admin():
    return ProjectActor(uuid.uuid4(), is_admin=True, is_manager=False)


def test_create_makes_actor_owner_and_member():
    repo = FakeProjectRepo()
    actor = _manager()
    project = CreateProject(repo).execute("Dự án A", None, actor)
    assert project.owner_id == actor.id
    assert (project.id, actor.id) in repo.members


def test_manager_cannot_update_someone_elses_project():
    repo = FakeProjectRepo()
    CreateProject(repo).execute("A", None, _manager())
    with pytest.raises(ProjectForbidden):
        UpdateProject(repo).execute(1, {"name": "B"}, _manager())


def test_owner_manager_can_update():
    repo = FakeProjectRepo()
    owner = _manager()
    CreateProject(repo).execute("A", None, owner)
    assert UpdateProject(repo).execute(1, {"name": "B"}, owner).name == "B"


def test_admin_can_update_any_project():
    repo = FakeProjectRepo()
    CreateProject(repo).execute("A", None, _manager())
    assert UpdateProject(repo).execute(1, {"name": "B"}, _admin()).name == "B"


def test_manager_owner_cannot_change_owner():
    repo = FakeProjectRepo(users={uuid.uuid4()})
    owner = _manager()
    CreateProject(repo).execute("A", None, owner)
    with pytest.raises(ProjectOwnerChangeForbidden):
        UpdateProject(repo).execute(1, {"owner_id": uuid.uuid4()}, owner)


def test_admin_cannot_change_owner_to_unknown_user():
    repo = FakeProjectRepo()
    CreateProject(repo).execute("A", None, _manager())
    with pytest.raises(OwnerNotFound):
        UpdateProject(repo).execute(1, {"owner_id": uuid.uuid4()}, _admin())


def test_manager_cannot_delete_someone_elses_project():
    repo = FakeProjectRepo()
    CreateProject(repo).execute("A", None, _manager())
    with pytest.raises(ProjectForbidden):
        DeleteProject(repo).execute(1, _manager())
    assert 1 in repo.projects


def test_get_unknown_project_raises_not_found():
    with pytest.raises(ProjectNotFound):
        GetProject(FakeProjectRepo()).execute(9999)


def test_list_clamps_limit_and_skip():
    repo = FakeProjectRepo()
    page = ListProjects(repo).execute(ProjectFilter(skip=-5, limit=10_000))
    assert repo.last_filter.skip == 0 and repo.last_filter.limit == 100
    assert page.has_more is False