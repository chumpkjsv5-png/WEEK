import uuid
from sqlalchemy import (
    Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','in_progress','completed')",
            name="ck_tasks_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    # FK bắt buộc -> phục vụ "group tasks by project"
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending", server_default="pending")

    # Enum đã được migration tạo sẵn trong DB -> create_type=False
    priority = Column(
        PGEnum(
            "Low", "Medium", "High",
            name="priority_enum",
            create_type=False,
        ),
        nullable=False,
        default="Medium",
        server_default="Medium",
    )

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # FK thật sự -> ràng buộc assignee_id phải tồn tại trong bảng users
    assignee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    due_date = Column(Date, nullable=True)

    # Quan hệ ORM -> cho phép task.project, task.assignee
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")