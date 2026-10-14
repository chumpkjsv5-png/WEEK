import uuid

from sqlalchemy import Column, String, DateTime, Boolean, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('admin','manager','member')", name="ck_users_role"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)

    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="member", server_default="member")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")
    memberships = relationship(
        "ProjectMember", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True,
    )