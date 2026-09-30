import uuid
from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.project_data import Project
from app.models.user_data import User
from app.schemas.project_schema import ProjectCreate, ProjectUpdate


def list_projects(
    db: Session,
    search: Optional[str] = None,
    owner_id: Optional[uuid.UUID] = None,
    created_after: Optional[date] = None,
    created_before: Optional[date] = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Project], int]:
    query = db.query(Project)

    if search and search.strip():
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                func.unaccent(Project.name).ilike(func.unaccent(pattern)),
                func.unaccent(Project.description).ilike(func.unaccent(pattern)),
            )
        )

    if owner_id is not None:
        query = query.filter(Project.owner_id == owner_id)

    if created_after:
        query = query.filter(
            Project.created_at >= datetime.combine(created_after, time.min)
        )

    if created_before:
        # Tính đến hết ngày được chọn
        end = datetime.combine(created_before + timedelta(days=1), time.min)
        query = query.filter(Project.created_at < end)

    total = query.count()
    items = (
        query.order_by(Project.created_at.desc(), Project.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, payload: ProjectCreate) -> Project:
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
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False

    db.delete(project)
    db.commit()
    return True