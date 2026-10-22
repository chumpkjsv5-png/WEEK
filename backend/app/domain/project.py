from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

DEFAULT_LIMIT = 10
MAX_LIMIT = 100  # giữ bằng MAX_LIMIT trong schemas/project_schema.py


@dataclass(frozen=True)
class ProjectActor:
    """Người thực hiện thao tác. Lõi chỉ cần biết vai trò đã quy đổi."""
    id: UUID
    is_admin: bool
    is_manager: bool


@dataclass
class Project:
    id: int
    name: str
    description: Optional[str]
    owner_id: Optional[UUID]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class NewProject:
    name: str
    description: Optional[str]
    owner_id: UUID


@dataclass(frozen=True)
class ProjectFilter:
    search: Optional[str] = None
    owner_id: Optional[UUID] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    skip: int = 0
    limit: int = DEFAULT_LIMIT


@dataclass
class ProjectPage:
    items: list[Project]
    total: int
    skip: int
    limit: int
    has_more: bool