from uuid import UUID

from app.application.ports.project_member_repository import ProjectMemberRepository
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


def _get_project_or_404(repo: ProjectMemberRepository, project_id: int) -> Project:
    project = repo.get_project(project_id)
    if project is None:
        raise ProjectNotFound("Project không tồn tại")
    return project


def _ensure_can_manage_members(project: Project, actor: ProjectActor) -> None:
    """Admin quản lý mọi project, manager chỉ project mình sở hữu."""
    if actor.is_admin:
        return
    if actor.is_manager and project.owner_id == actor.id:
        return
    raise ProjectMemberForbidden(
        "Bạn chỉ được quản lý thành viên của project do mình sở hữu"
    )


class ListMembers:
    def __init__(self, repo: ProjectMemberRepository):
        self.repo = repo

    def execute(self, project_id: int) -> list[Member]:
        _get_project_or_404(self.repo, project_id)
        return self.repo.list_members(project_id)


class SearchUsersToAdd:
    def __init__(self, repo: ProjectMemberRepository):
        self.repo = repo

    def execute(
        self, project_id: int, q: str, actor: ProjectActor, limit: int = 10
    ) -> list[MemberUser]:
        project = _get_project_or_404(self.repo, project_id)
        _ensure_can_manage_members(project, actor)
        q = q.strip()
        if not q:
            return []
        return self.repo.search_candidates(project_id, q, limit)


class AddMember:
    def __init__(self, repo: ProjectMemberRepository):
        self.repo = repo

    def execute(self, project_id: int, user_id: UUID, actor: ProjectActor) -> Member:
        project = _get_project_or_404(self.repo, project_id)
        _ensure_can_manage_members(project, actor)
        if not self.repo.user_exists(user_id):
            raise UserNotFound("User không tồn tại")
        if self.repo.get_member(project_id, user_id) is not None:
            raise MemberAlreadyExists("User đã là thành viên của project")
        return self.repo.add(project_id, user_id)


class RemoveMember:
    def __init__(self, repo: ProjectMemberRepository):
        self.repo = repo

    def execute(self, project_id: int, user_id: UUID, actor: ProjectActor) -> None:
        project = _get_project_or_404(self.repo, project_id)
        _ensure_can_manage_members(project, actor)
        if project.owner_id == user_id:
            raise CannotRemoveOwner("Không thể gỡ chủ sở hữu khỏi project")
        if self.repo.get_member(project_id, user_id) is None:
            raise MemberNotFound("User không phải thành viên của project")

        open_tasks = self.repo.count_open_tasks(project_id, user_id)
        if open_tasks:
            raise MemberHasOpenTasks(
                f"Thành viên còn {open_tasks} task chưa hoàn thành, "
                "hãy hoàn thành hoặc giao lại trước khi gỡ"
            )
        self.repo.remove(project_id, user_id)