import uuid

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # 1 user -> N project (owner)
    projects = relationship("Project", back_populates="owner")
    # 1 user -> N task (assignee)
    tasks = relationship("Task", back_populates="assignee")

    # User
    memberships = relationship(
        "ProjectMember", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True,
    )
