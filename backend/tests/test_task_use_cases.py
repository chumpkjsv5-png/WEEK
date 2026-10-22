import uuid

import pytest

from app.application.use_cases.task_use_cases import (
    CompleteTask,
    CreateTask,
    ListTasks,
    UpdateTask,
)
from app.domain.errors import (
    AssigneeNotProjectMember,
    ProjectNotFound,
    TaskNotAssignedToYou,
    TaskNotFound,
    TaskStatusOnly,
)
from app.domain.task import Actor, NewTask, Task, TaskFilter


class FakeTaskRepo:
    def __init__(self, projects=(), users=(), members=()):
        self.projects, self.users, self.members = set(projects), set(users), set(members)
        self.tasks = {}
        self.last_filter = None

    def project_exists(self, project_id):
        return project_id in self.projects

    def user_exists(self, user_id):
        return user_id in self.users

    def is_project_member(self, project_id, user_id):
        return (project_id, user_id) in self.members

    def add(self, new):
        task = Task(
            id=len(self.tasks) + 1, project_id=new.project_id, title=new.title,
            description=new.description, status=new.status, priority=new.priority,
            assignee_id=new.assignee_id, due_date=new.due_date,
        )
        self.tasks[task.id] = task
        return task

    def get(self, task_id):
        return self.tasks.get(task_id)

    def search(self, f):
        self.last_filter = f
        items = list(self.tasks.values())
        return items[f.skip:f.skip + f.limit], len(items)

    def update(self, task_id, changes):
        task = self.tasks[task_id]
        for key, value in changes.items():
            setattr(task, key, value)
        return task

    def delete(self, task_id):
        self.tasks.pop(task_id, None)


def _new(project_id=1, assignee_id=None):
    return NewTask(project_id, "Việc A", None, "pending", "Medium", assignee_id, None)


def test_create_fails_when_project_missing():
    with pytest.raises(ProjectNotFound):
        CreateTask(FakeTaskRepo()).execute(_new(project_id=99))


def test_create_fails_when_assignee_not_member():
    u = uuid.uuid4()
    repo = FakeTaskRepo(projects={1}, users={u})  # u tồn tại nhưng không thuộc project 1
    with pytest.raises(AssigneeNotProjectMember):
        CreateTask(repo).execute(_new(assignee_id=u))


def test_member_cannot_update_task_of_someone_else():
    owner, other = uuid.uuid4(), uuid.uuid4()
    repo = FakeTaskRepo(projects={1}, users={owner, other}, members={(1, owner)})
    CreateTask(repo).execute(_new(assignee_id=owner))
    with pytest.raises(TaskNotAssignedToYou):
        UpdateTask(repo).execute(1, {"status": "completed"}, Actor(other, is_member=True))


def test_member_can_only_change_status():
    me = uuid.uuid4()
    repo = FakeTaskRepo(projects={1}, users={me}, members={(1, me)})
    CreateTask(repo).execute(_new(assignee_id=me))
    with pytest.raises(TaskStatusOnly):
        UpdateTask(repo).execute(1, {"title": "đổi tên"}, Actor(me, is_member=True))
    done = UpdateTask(repo).execute(1, {"status": "in_progress"}, Actor(me, is_member=True))
    assert done.status == "in_progress"


def test_complete_task_by_assignee():
    me = uuid.uuid4()
    repo = FakeTaskRepo(projects={1}, users={me}, members={(1, me)})
    CreateTask(repo).execute(_new(assignee_id=me))
    assert CompleteTask(repo).execute(1, Actor(me, is_member=True)).status == "completed"


def test_update_unknown_task_raises_not_found():
    with pytest.raises(TaskNotFound):
        UpdateTask(FakeTaskRepo()).execute(9, {"status": "completed"}, Actor(uuid.uuid4(), False))


def test_list_clamps_limit_and_skip():
    repo = FakeTaskRepo()
    page = ListTasks(repo).execute(TaskFilter(skip=-5, limit=10_000))
    assert repo.last_filter.skip == 0 and repo.last_filter.limit == 100
    assert page.has_more is False