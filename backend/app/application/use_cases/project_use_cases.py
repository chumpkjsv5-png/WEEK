from dataclasses import replace
from typing import Any, Optional

from app.application.ports.project_repository import ProjectRepository
from app.domain.errors import (
    OwnerNotFound,
    ProjectForbidden,
    ProjectNotFound,
    ProjectOwnerChangeForbidden,
)
from app.domain.project import (
    MAX_LIMIT,
    NewProject,
    Project,
    ProjectActor,
    ProjectFilter,
    ProjectPage,
)


def _get_or_404(repo: ProjectRepository, project_id: int) -> Project:
    project = repo.get(project_id)
    if project is None:
        raise ProjectNotFound("Project không tồn tại")
    return project


def _ensure_can_modify(
    project: Project, actor: ProjectActor, action: str = "thao tác với"
) -> None:
    """Admin quản lý mọi project, manager chỉ quản lý project mình sở hữu."""
    if actor.is_admin:
        return
    if actor.is_manager and project.owner_id == actor.id:
        return
    raise ProjectForbidden(
        f"Bạn không có quyền {action} project do người khác sở hữu"
    )


class ListProjects:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(self, f: ProjectFilter) -> ProjectPage:
        # Chốt chặn cho trường hợp gọi từ nơi không qua validation của router
        skip = max(f.skip, 0)
        limit = min(max(f.limit, 1), MAX_LIMIT)

        items, total = self.projects.search(replace(f, skip=skip, limit=limit))
        return ProjectPage(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + len(items) < total,
        )


class GetProject:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(self, project_id: int) -> Project:
        return _get_or_404(self.projects, project_id)


class CreateProject:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(
        self, name: str, description: Optional[str], actor: ProjectActor
    ) -> Project:
        # Người tạo là owner, và tự động là thành viên
        return self.projects.add_with_owner_member(
            NewProject(name=name, description=description, owner_id=actor.id)
        )


class UpdateProject:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(
        self, project_id: int, changes: dict[str, Any], actor: ProjectActor
    ) -> Project:
        project = _get_or_404(self.projects, project_id)  # 404 trước
        _ensure_can_modify(project, actor, "chỉnh sửa")   # rồi 403

        if "owner_id" in changes:
            if not actor.is_admin:
                raise ProjectOwnerChangeForbidden(
                    "Chỉ admin mới được đổi chủ sở hữu project"
                )
            new_owner = changes["owner_id"]
            if new_owner is not None and not self.projects.user_exists(new_owner):
                raise OwnerNotFound("owner_id không tồn tại")

        return self.projects.update(project_id, changes)


class DeleteProject:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(self, project_id: int, actor: ProjectActor) -> None:
        project = _get_or_404(self.projects, project_id)  # 404 trước
        _ensure_can_modify(project, actor, "xóa")         # admin, hoặc manager là chủ
        self.projects.delete(project_id)