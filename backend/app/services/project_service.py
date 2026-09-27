from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_data import Project
from app.models.user_data import User
from app.schemas.project_schema import ProjectCreate


def list_projects(db: Session):
    return db.scalars(select(Project).order_by(Project.created_at.desc())).all()


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.get(Project, project_id)


def create_project(db: Session, payload: ProjectCreate) -> Project:
    if payload.owner_id is not None:
        owner = db.get(User, payload.owner_id)
        if not owner:
            raise ValueError("owner_id không tồn tại")

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project