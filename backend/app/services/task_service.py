from sqlalchemy.orm import Session
from sqlalchemy import select, func

from typing import Optional
from uuid import UUID
from datetime import date

from app.models.task_data import Task
from app.models.project_data import Project
from app.models.user_data import User
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskStatus


def create_task(db: Session, task_data: TaskCreate) -> Task:
    project = db.query(Project).filter(Project.id == task_data.project_id).first()
    if not project:
        raise ValueError("project_id không tồn tại")

    if task_data.assignee_id is not None:
        assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not assignee:
            raise ValueError("assignee_id không tồn tại")

    new_task = Task(**task_data.model_dump())
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
    assignee_id: Optional[UUID] = None,
    due_before: Optional[date] = None,
    due_after: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> dict:
    query = select(Task)

    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if search:
        query = query.where(Task.title.ilike(f"%{search}%"))
    if status:
        query = query.where(Task.status == status)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
    if due_before:
        query = query.where(Task.due_date <= due_before)
    if due_after:
        query = query.where(Task.due_date >= due_after)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0   

    query = query.order_by(Task.due_date.asc().nulls_last(), Task.id.asc())
    query = query.offset(skip).limit(limit)

    items = db.scalars(query).all()

    return {"items": items, "total": total, "skip": skip, "limit": limit}


def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    task = get_task(db, task_id)
    if not task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)

    if "project_id" in update_data and update_data["project_id"] is not None:
        project = db.query(Project).filter(Project.id == update_data["project_id"]).first()
        if not project:
            raise ValueError("project_id không tồn tại")

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        assignee = db.query(User).filter(User.id == update_data["assignee_id"]).first()
        if not assignee:
            raise ValueError("assignee_id không tồn tại")

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def complete_task(db: Session, task_id: int) -> Optional[Task]:
    task = get_task(db, task_id)
    if not task:
        return None

    task.status = TaskStatus.completed
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