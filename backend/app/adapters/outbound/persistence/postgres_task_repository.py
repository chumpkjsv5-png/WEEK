from dataclasses import asdict
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.domain.errors import TaskNotFound
from app.domain.task import NewTask, Task, TaskFilter, TaskPriority
from app.models.project_data import Project
from app.models.project_member import ProjectMember
from app.models.task_data import Task as TaskRow
from app.models.user_data import User

_UPDATABLE = {
    "project_id", "title", "description", "status",
    "priority", "assignee_id", "due_date",
}

# Xếp hạng priority bằng CASE: chạy đúng dù cột là String hay native ENUM.
# DESC => High -> Medium -> Low (priority null xếp cuối)
PRIORITY_RANK = case(
    (TaskRow.priority == TaskPriority.HIGH, 3),
    (TaskRow.priority == TaskPriority.MEDIUM, 2),
    (TaskRow.priority == TaskPriority.LOW, 1),
    else_=0,
)


def _escape_like(text: str) -> str:
    """Escape ký tự đặc biệt của LIKE để % và _ được hiểu là ký tự thường."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _to_domain(row: TaskRow) -> Task:
    return Task(
        id=row.id,
        project_id=row.project_id,
        title=row.title,
        description=row.description,
        status=row.status,
        priority=row.priority,
        assignee_id=row.assignee_id,
        due_date=row.due_date,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresTaskRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- kiểm tra tham chiếu ---
    def project_exists(self, project_id: int) -> bool:
        return self.db.get(Project, project_id) is not None

    def user_exists(self, user_id: UUID) -> bool:
        return self.db.get(User, user_id) is not None

    def is_project_member(self, project_id: int, user_id: UUID) -> bool:
        found = self.db.scalar(
            select(ProjectMember.user_id).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        return found is not None

    # --- CRUD ---
    def add(self, new: NewTask) -> Task:
        row = TaskRow(**asdict(new))
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return _to_domain(row)

    def get(self, task_id: int) -> Optional[Task]:
        row = self.db.get(TaskRow, task_id)
        return _to_domain(row) if row else None

    def update(self, task_id: int, changes: dict[str, Any]) -> Task:
        row = self.db.get(TaskRow, task_id)
        if row is None:
            raise TaskNotFound("Task không tồn tại")
        for key, value in changes.items():
            if key in _UPDATABLE:
                setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return _to_domain(row)

    def delete(self, task_id: int) -> None:
        row = self.db.get(TaskRow, task_id)
        if row is not None:
            self.db.delete(row)
            self.db.commit()

    def search(self, f: TaskFilter) -> tuple[list[Task], int]:
        filters = []
        if f.project_id is not None:
            filters.append(TaskRow.project_id == f.project_id)
        if f.search:
            filters.append(TaskRow.title.ilike(f"%{_escape_like(f.search)}%", escape="\\"))
        if f.status:
            filters.append(TaskRow.status == f.status)
        if f.priority:
            filters.append(TaskRow.priority == f.priority)
        if f.assignee_id:
            filters.append(TaskRow.assignee_id == f.assignee_id)
        if f.due_before:
            filters.append(TaskRow.due_date < f.due_before)
        if f.due_after:
            filters.append(TaskRow.due_date > f.due_after)

        total = self.db.scalar(
            select(func.count()).select_from(TaskRow).where(*filters)
        ) or 0

        # Không có dữ liệu hoặc skip vượt quá tổng: bỏ qua query lấy dữ liệu
        if total == 0 or f.skip >= total:
            return [], total

        order = [TaskRow.due_date.asc().nulls_last(), TaskRow.id.asc()]  # id làm tiebreaker
        if f.sort_by_priority:
            order.insert(0, PRIORITY_RANK.desc())

        rows = self.db.scalars(
            select(TaskRow).where(*filters).order_by(*order).offset(f.skip).limit(f.limit)
        ).all()
        return [_to_domain(r) for r in rows], total