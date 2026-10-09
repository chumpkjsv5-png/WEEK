from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.task_schema import (
    TaskCreate, TaskFilterParams, TaskListOut, TaskOut, TaskUpdate,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(task: TaskCreate, db: DbSession):
    return task_service.create_task(db, task)


@router.get("/", response_model=TaskListOut)
def get_tasks(params: Annotated[TaskFilterParams, Query()], db: DbSession):
    return task_service.get_tasks(db, **params.model_dump())


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: DbSession):
    return task_service.get_task(db, task_id)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db: DbSession):
    return task_service.update_task(db, task_id, task_update)


@router.patch("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, db: DbSession):
    return task_service.complete_task(db, task_id)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: DbSession):
    task_service.delete_task(db, task_id)