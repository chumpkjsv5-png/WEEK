from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.task_schema import (
    TaskCreate,
    TaskFilterParams,
    TaskListOut,
    TaskOut,
    TaskUpdate,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(task: TaskCreate, db: DbSession):
    try:
        return task_service.create_task(db, task)
    except LookupError as e:  # project/assignee không tồn tại
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:  # dữ liệu sai
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=TaskListOut)
def get_tasks(params: Annotated[TaskFilterParams, Query()], db: DbSession):
    try:
        return task_service.get_tasks(db, **params.model_dump())
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: DbSession):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db: DbSession):
    try:
        task = task_service.update_task(db, task_id, task_update)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, db: DbSession):
    task = task_service.complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: DbSession):
    if not task_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")