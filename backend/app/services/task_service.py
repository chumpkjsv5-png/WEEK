from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID
 
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
 
from app.models.project_data import Project
from app.models.task_data import Task
from app.models.user_data import User
from app.schemas.task_schema import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskUpdate,
)
 
# Xếp hạng priority bằng CASE: chạy đúng dù cột là String hay native ENUM.
# DESC => High -> Medium -> Low (priority null xếp cuối)
PRIORITY_RANK = case(
    (Task.priority == TaskPriority.High.value, 3),
    (Task.priority == TaskPriority.Medium.value, 2),
    (Task.priority == TaskPriority.Low.value, 1),
    else_=0,
)
 
 
def _to_db(data: dict) -> dict:
    """Đổi Enum thành giá trị thường trước khi lưu DB."""
    return {k: (v.value if isinstance(v, Enum) else v) for k, v in data.items()}
 
 
def _escape_like(text: str) -> str:
    """Escape ký tự đặc biệt của LIKE để % và _ được hiểu là ký tự thường."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
 
 
def _ensure_refs_exist(
    db: Session,
    project_id: Optional[int] = None,
    assignee_id: Optional[UUID] = None,
) -> None:
    """Kiểm tra project/assignee tồn tại (db.get dùng identity map nên nhẹ hơn query)."""
    if project_id is not None and db.get(Project, project_id) is None:
        raise LookupError("project_id không tồn tại")
    if assignee_id is not None and db.get(User, assignee_id) is None:
        raise LookupError("assignee_id không tồn tại")
 
 
def create_task(db: Session, task_data: TaskCreate) -> Task:
    _ensure_refs_exist(db, task_data.project_id, task_data.assignee_id)
 
    new_task = Task(**_to_db(task_data.model_dump()))
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
 
 
def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.get(Task, task_id)
 
 
def get_tasks(
    db: Session,
    project_id: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[UUID] = None,
    due_before: Optional[date] = None,
    due_after: Optional[date] = None,
    sort_by_priority: bool = False,
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> dict:
    # Chốt chặn cho trường hợp gọi từ nơi không qua validation của router
    skip = max(skip, 0)
    limit = min(max(limit, 1), MAX_LIMIT)
 
    _ensure_refs_exist(db, assignee_id=assignee_id)
 
    filters = []
    if project_id is not None:
        filters.append(Task.project_id == project_id)
    if search:
        filters.append(Task.title.ilike(f"%{_escape_like(search)}%", escape="\\"))
    if status:
        filters.append(Task.status == status.value)
    if priority:
        filters.append(Task.priority == priority.value)
    if assignee_id:
        filters.append(Task.assignee_id == assignee_id)
    if due_before:
        filters.append(Task.due_date < due_before)
    if due_after:
        filters.append(Task.due_date > due_after)
 
    total = db.scalar(select(func.count()).select_from(Task).where(*filters)) or 0
 
    # Không có dữ liệu hoặc skip vượt quá tổng: bỏ qua query lấy dữ liệu
    if total == 0 or skip >= total:
        return {"items": [], "total": total, "skip": skip, "limit": limit, "has_more": False}
 
    order = [Task.due_date.asc().nulls_last(), Task.id.asc()]  # id làm tiebreaker
    if sort_by_priority:
        order.insert(0, PRIORITY_RANK.desc())
 
    items = db.scalars(
        select(Task).where(*filters).order_by(*order).offset(skip).limit(limit)
    ).all()
 
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(items) < total,
    }
 
 
def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    task = get_task(db, task_id)
    if not task:
        return None
 
    update_data = task_update.model_dump(exclude_unset=True)
 
    _ensure_refs_exist(
        db,
        project_id=update_data.get("project_id"),
        assignee_id=update_data.get("assignee_id"),
    )
 
    for field, value in _to_db(update_data).items():
        setattr(task, field, value)
 
    db.commit()
    db.refresh(task)
    return task
 
 
def complete_task(db: Session, task_id: int) -> Optional[Task]:
    task = get_task(db, task_id)
    if not task:
        return None
 
    task.status = TaskStatus.completed.value
    db.commit()
    db.refresh(task)
    return task
 
 
def delete_task(db: Session, task_id: int) -> bool:
    task = get_task(db, task_id)
    if not task:
        return False
 
    db.delete(task)
    db.commit()
    return True