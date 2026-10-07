# app/models/project_member.py
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    project = relationship("Project", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

    # PK kép (project_id, user_id) đã tối ưu tìm theo project_id.
    # Index này tối ưu chiều ngược lại: "user này thuộc những project nào".
    __table_args__ = (Index("ix_project_members_user_id", "user_id"),)  