from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.pending
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
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