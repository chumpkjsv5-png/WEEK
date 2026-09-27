from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskBase(BaseModel):
    project_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.pending
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    project_id: Optional[int] = None          # ← thêm: cho phép chuyển task sang project khác
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskOut(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskListOut(BaseModel):
    items: List[TaskOut]
    total: int
    skip: int
    limit: int