# app/services/project_member_service.py
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.project_data import Project
from app.models.user_data import User
from app.models.project_member import ProjectMember


def _get_project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    return project


def list_members(db: Session, project_id: int):
    _get_project(db, project_id)
    stmt = (
        select(ProjectMember)
        .options(joinedload(ProjectMember.user))   # lấy luôn user, tránh query lặp
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.created_at)
    )
    return db.scalars(stmt).all()


def add_member(db: Session, project_id: int, user_id):
    _get_project(db, project_id)
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User không tồn tại")
    if db.get(ProjectMember, (project_id, user_id)):
        raise HTTPException(status_code=409, detail="User đã là thành viên của project")

    member = ProjectMember(project_id=project_id, user_id=user_id)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:            # phòng hai request thêm cùng lúc
        db.rollback()
        raise HTTPException(status_code=409, detail="User đã là thành viên của project")
    db.refresh(member)
    return member


def remove_member(db: Session, project_id: int, user_id) -> None:
    project = _get_project(db, project_id)
    if project.owner_id == user_id:
        raise HTTPException(status_code=409, detail="Không thể gỡ chủ sở hữu khỏi project")

    member = db.get(ProjectMember, (project_id, user_id))
    if not member:
        raise HTTPException(status_code=404, detail="User không phải thành viên của project")
    db.delete(member)
    db.commit()