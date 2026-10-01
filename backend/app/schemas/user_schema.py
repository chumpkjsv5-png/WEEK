from uuid import UUID
from pydantic import BaseModel


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    model_config = {"from_attributes": True}