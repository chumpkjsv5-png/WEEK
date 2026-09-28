from typing import Optional
from sqlalchemy.orm import Session

from app.models.project_data import Project
from app.models.user_data import User
from app.schemas.project_schema import ProjectCreate, ProjectUpdate


def list_projects(db: Session) -> list[Project]:
    """Get all projects ordered by created_at descending"""
    return db.query(Project).order_by(Project.created_at.desc()).all()


def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get a single project by id"""
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, payload: ProjectCreate) -> Project:
    """Create a new project"""
    # Validate owner_id exists if provided
    if payload.owner_id is not None:
        owner = db.query(User).filter(User.id == payload.owner_id).first()
        if not owner:
            raise ValueError("owner_id không tồn tại")

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session,
    project_id: int,
    payload: ProjectUpdate
) -> Optional[Project]:
    """Update a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    # Validate owner_id if provided
    if payload.owner_id is not None:
        owner = db.query(User).filter(User.id == payload.owner_id).first()
        if not owner:
            raise ValueError("owner_id không tồn tại")

    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    """Delete a project (cascades to tasks)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False

    db.delete(project)
    db.commit()
    return True