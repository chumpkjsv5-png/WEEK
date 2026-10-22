from typing import Optional, Protocol
from uuid import UUID

from app.domain.project import Project
from app.domain.project_member import Member, MemberUser


class ProjectMemberRepository(Protocol):
    def get_project(self, project_id: int) -> Optional[Project]: ...

    def list_members(self, project_id: int) -> list[Member]: ...

    def search_candidates(
        self, project_id: int, q: str, limit: int
    ) -> list[MemberUser]:
        """User khớp tên/email và chưa là thành viên của project."""

    def user_exists(self, user_id: UUID) -> bool: ...

    def get_member(self, project_id: int, user_id: UUID) -> Optional[Member]: ...

    def add(self, project_id: int, user_id: UUID) -> Member:
        """Ném MemberAlreadyExists nếu hai request thêm cùng lúc."""

    def remove(self, project_id: int, user_id: UUID) -> None: ...

    def count_open_tasks(self, project_id: int, user_id: UUID) -> int: ...