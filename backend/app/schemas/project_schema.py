import uuid
from datetime import datetime,date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )
    owner_id: Optional[uuid.UUID] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )
    owner_id: Optional[uuid.UUID] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

class ProjectFilterParams(BaseModel):
    search: Optional[str] = Field(default=None, max_length=100)
    owner_id: Optional[uuid.UUID] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def check_date_range(self):
        if (
            self.created_after
            and self.created_before
            and self.created_after > self.created_before
        ):
            raise ValueError("created_after phải nhỏ hơn hoặc bằng created_before")
        return self


class ProjectListOut(BaseModel):
    items: list[ProjectOut]
    total: int