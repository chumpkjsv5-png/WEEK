from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskOut, TaskListOut, TaskStatus
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        return task_service.create_task(db, task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=TaskListOut)
def get_tasks(
    project_id: Optional[int] = None,          # Story 1: group by project
    search: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    assignee_id: Optional[UUID] = None,
    due_before: Optional[date] = None,           # Story 2: filter theo date
    due_after: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return task_service.get_tasks(
        db,
        project_id=project_id,
        search=search,
        status=status,
        assignee_id=assignee_id,
        due_before=due_before,
        due_after=due_after,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    try:
        task = task_service.update_task(db, task_id, task_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = task_service.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}