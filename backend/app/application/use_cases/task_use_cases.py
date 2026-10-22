from dataclasses import replace
from typing import Any, Optional
from uuid import UUID

from app.application.ports.task_repository import TaskRepository
from app.domain.errors import (
    AssigneeNotFound,
    AssigneeNotProjectMember,
    ProjectNotFound,
    TaskNotAssignedToYou,
    TaskNotFound,
    TaskStatusOnly,
)
from app.domain.task import (
    MAX_LIMIT,
    Actor,
    NewTask,
    Task,
    TaskFilter,
    TaskPage,
    TaskStatus,
)


def _ensure_refs_exist(
    repo: TaskRepository,
    project_id: Optional[int] = None,
    assignee_id: Optional[UUID] = None,
) -> None:
    if project_id is not None and not repo.project_exists(project_id):
        raise ProjectNotFound("project_id không tồn tại")
    if assignee_id is not None and not repo.user_exists(assignee_id):
        raise AssigneeNotFound("assignee_id không tồn tại")


def _ensure_assignee_is_member(
    repo: TaskRepository, project_id: Optional[int], assignee_id: Optional[UUID]
) -> None:
    if project_id is None or assignee_id is None:
        return
    if not repo.is_project_member(project_id, assignee_id):
        raise AssigneeNotProjectMember("assignee_id không phải thành viên của project")


def _ensure_member_can_touch(task: Task, actor: Actor) -> None:
    """Member chỉ được thao tác trên task giao cho mình."""
    if actor.is_member and task.assignee_id != actor.id:
        raise TaskNotAssignedToYou("Bạn chỉ được cập nhật task được giao cho mình")


def _get_or_404(repo: TaskRepository, task_id: int) -> Task:
    task = repo.get(task_id)
    if task is None:
        raise TaskNotFound("Task không tồn tại")
    return task


class CreateTask:
    def __init__(self, tasks: TaskRepository):
        self.tasks = tasks

    def execute(self, new: NewTask) -> Task:
        _ensure_refs_exist(self.tasks, new.project_id, new.assignee_id)
        _ensure_assignee_is_member(self.tasks, new.project_id, new.assignee_id)
        return self.tasks.add(new)


class GetTask:
    def __init__(self, tasks: TaskRepository):
        self.tasks = tasks

    def execute(self, task_id: int) -> Task:
        return _get_or_404(self.tasks, task_id)


class ListTasks:
    def __init__(self, tasks: TaskRepository):
        self.tasks = tasks

    def execute(self, f: TaskFilter) -> TaskPage:
        # Chốt chặn cho trường hợp gọi từ nơi không qua validation của router
        skip = max(f.skip, 0)
        limit = min(max(f.limit, 1), MAX_LIMIT)

        _ensure_refs_exist(self.tasks, assignee_id=f.assignee_id)

        items, total = self.tasks.search(replace(f, skip=skip, limit=limit))
        return TaskPage(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + len(items) < total,
        )


class UpdateTask:
    def __init__(self, tasks: TaskRepository):
        self.tasks = tasks

    def execute(self, task_id: int, changes: dict[str, Any], actor: Actor) -> Task:
        task = _get_or_404(self.tasks, task_id)

        # Quyền: member chỉ sửa task giao cho mình, và chỉ được đổi status
        _ensure_member_can_touch(task, actor)
        if actor.is_member and set(changes) - {"status"}:
            raise TaskStatusOnly("Bạn chỉ được đổi trạng thái task")

        # Phần dưới được bổ sung vì bản dán bị cụt: kiểm tra tham chiếu mới
        if "project_id" in changes or "assignee_id" in changes:
            _ensure_refs_exist(
                self.tasks, changes.get("project_id"), changes.get("assignee_id")
            )
            _ensure_assignee_is_member(
                self.tasks,
                changes.get("project_id", task.project_id),
                changes.get("assignee_id", task.assignee_id),
            )

        return self.tasks.update(task_id, changes)


class CompleteTask:
    def __init__(self, tasks: TaskRepository):
        self.tasks = tasks

    def execute(self, task_id: int, actor: Actor) -> Task:
        task = _get_or_404(self.tasks, task_id)
        _ensure_member_can_touch(task, actor)
        return self.tasks.update(task_id, {"status": TaskStatus.COMPLETED})


class DeleteTask:
    def __init__(self, tasks: TaskRepository):
        self.tasks = tasks

    def execute(self, task_id: int) -> None:
        _get_or_404(self.tasks, task_id)
        self.tasks.delete(task_id)