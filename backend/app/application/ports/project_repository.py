from typing import Any, Optional, Protocol
from uuid import UUID

from app.domain.project import NewProject, Project, ProjectFilter


class ProjectRepository(Protocol):
    def user_exists(self, user_id: UUID) -> bool: ...

    def get(self, project_id: int) -> Optional[Project]: ...

    def search(self, f: ProjectFilter) -> tuple[list[Project], int]: ...

    def add_with_owner_member(self, new: NewProject) -> Project:
        """Tạo project và thêm owner làm thành viên trong cùng một transaction."""

    def update(self, project_id: int, changes: dict[str, Any]) -> Project: ...

    def delete(self, project_id: int) -> None: ...