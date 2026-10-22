from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

DEFAULT_LIMIT = 20
MAX_LIMIT = 100  # giữ bằng MAX_LIMIT trong schemas/task_schema.py


class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass(frozen=True)
class Actor:
    """Người thực hiện thao tác. Lõi chỉ cần biết có phải member hay không."""
    id: UUID
    is_member: bool


@dataclass
class Task:
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    assignee_id: Optional[UUID]
    due_date: Optional[date]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class NewTask:
    project_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    assignee_id: Optional[UUID]
    due_date: Optional[date]


@dataclass(frozen=True)
class TaskFilter:
    project_id: Optional[int] = None
    search: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[UUID] = None
    due_after: Optional[date] = None
    due_before: Optional[date] = None
    sort_by_priority: bool = False
    skip: int = 0
    limit: int = DEFAULT_LIMIT


@dataclass
class TaskPage:
    items: list[Task]
    total: int
    skip: int
    limit: int
    has_more: bool