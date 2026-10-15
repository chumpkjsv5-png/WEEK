import uuid

from pydantic import BaseModel, ConfigDict


class UserBrief(BaseModel):
    """Thông tin tối thiểu để chọn người (không có role, password)."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str


class UserBriefList(BaseModel):
    items: list[UserBrief]
    total: int