import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

DEFAULT_LIMIT = 10
MAX_LIMIT = 100


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)
    owner_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def check_update(self):
        if not self.model_fields_set:
            raise ValueError("Cần ít nhất một trường để cập nhật")
        # name là cột bắt buộc nên không cho set null
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name không được để null")
        return self


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class ProjectFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    search: Optional[str] = Field(default=None, max_length=100)
    owner_id: Optional[uuid.UUID] = None
    created_after: Optional[date] = None   # created_at >= đầu ngày created_after
    created_before: Optional[date] = None  # created_at <= hết ngày created_before
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)

    @field_validator("search")
    @classmethod
    def empty_search_to_none(cls, v):
        return v or None

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
    skip: int
    limit: int
    has_more: bool