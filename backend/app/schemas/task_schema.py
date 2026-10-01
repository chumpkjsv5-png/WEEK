from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from enum import Enum


class TaskPriority(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"



class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskBase(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.pending
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[UUID] = None  
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    model_config = ConfigDict(str_strip_whitespace=True)

    project_id: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    project_id: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: TaskPriority = TaskPriority.Medium
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None

    @model_validator(mode="after")
    def check_update(self):
        if not self.model_fields_set:
            raise ValueError("Cần ít nhất một trường để cập nhật")

        # Các trường này không được phép null; chỉ description/assignee_id/due_date được xóa
        for name in ("project_id", "title", "status","priority"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} không được để null")
        return self


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class TaskListOut(BaseModel):
    items: List[TaskOut]
    total: int
    skip: int
    limit: int


class TaskFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    search: Optional[str] = Field(default=None, max_length=100)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    project_id: Optional[int] = Field(default=None, ge=1)
    assignee_id: Optional[UUID] = None
    due_after: Optional[date] = None
    due_before: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)

    @field_validator("search")
    @classmethod
    def empty_search_to_none(cls, v):
        return v or None

    @model_validator(mode="after")
    def check_date_range(self):
        if self.due_after and self.due_before and self.due_after > self.due_before:
            raise ValueError("due_after phải nhỏ hơn hoặc bằng due_before")
        return self