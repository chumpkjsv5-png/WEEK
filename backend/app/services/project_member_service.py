# app/services/project_member_service.py
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.models.project_data import Project
from app.models.project_member import ProjectMember
from app.models.task_data import Task
from app.models.user_data import User
from app.schemas.task_schema import TaskStatus


def _get_project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise NotFoundError("Project không tồn tại")
    return project


def list_members(db: Session, project_id: int):
    _get_project(db, project_id)
    stmt = (
        select(ProjectMember)
        .options(joinedload(ProjectMember.user))  # lấy luôn user, tránh query lặp
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.created_at)
    )
    return db.scalars(stmt).all()


def search_users_to_add(db: Session, project_id: int, q: str, limit: int = 10):
    """Tìm user theo tên/email để thêm vào project.

    Loại các user đã là thành viên của project.
    """
    _get_project(db, project_id)

    q = q.strip()
    if not q:
        return []

    # escape ký tự đặc biệt của LIKE để gõ % hoặc _ không bị match bậy
    escaped = q.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
    pattern = f"%{escaped}%"

    already_member = select(ProjectMember.user_id).where(
        ProjectMember.project_id == project_id
    )

    stmt = (
        select(User)
        .where(
            or_(
                User.full_name.ilike(pattern, escape="\\"),
                User.email.ilike(pattern, escape="\\"),
            ),
            User.id.not_in(already_member),
        )
        .order_by(User.full_name)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def add_member(db: Session, project_id: int, user_id):
    _get_project(db, project_id)
    if not db.get(User, user_id):
        raise NotFoundError("User không tồn tại")
    if db.get(ProjectMember, (project_id, user_id)):
        raise ConflictError("User đã là thành viên của project")

    member = ProjectMember(project_id=project_id, user_id=user_id)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:  # phòng hai request thêm cùng lúc
        db.rollback()
        raise ConflictError("User đã là thành viên của project")
    db.refresh(member)
    return member


def remove_member(db: Session, project_id: int, user_id) -> None:
    project = _get_project(db, project_id)
    if project.owner_id == user_id:
        raise ConflictError("Không thể gỡ chủ sở hữu khỏi project")

    member = db.get(ProjectMember, (project_id, user_id))
    if not member:
        raise NotFoundError("User không phải thành viên của project")

    open_tasks = db.scalar(
        select(func.count())
        .select_from(Task)
        .where(
            Task.project_id == project_id,
            Task.assignee_id == user_id,
            Task.status != TaskStatus.completed.value,
        )
    )
    if open_tasks:
        raise ConflictError(
            f"Thành viên còn {open_tasks} task chưa hoàn thành, "
            "hãy hoàn thành hoặc giao lại trước khi gỡ"
        )

    db.delete(member)
    db.commit()