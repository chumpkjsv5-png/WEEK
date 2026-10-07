# app/schemas/project_member_schema.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class MemberCreate(BaseModel):
    user_id: UUID


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    user_id: UUID
    created_at: datetime
    user: UserBrief