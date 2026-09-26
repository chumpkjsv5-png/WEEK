from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.models.task_data import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskStatus


def create_task(db: Session, task_data: TaskCreate) -> Task:
    new_task = Task(**task_data.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(
    db: Session,
    search: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    assignee_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Task]:
    query = db.query(Task)

    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    if status:
        query = query.filter(Task.status == status)

    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    return query.offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    task = get_task(db, task_id)
    if not task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
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