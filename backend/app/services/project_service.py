# app/services/project_service.py
import uuid
from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.core.permissions import ADMIN, MANAGER
from app.models.project_data import Project
from app.models.project_member import ProjectMember
from app.models.user_data import User
from app.schemas.project_schema import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    ProjectCreate,
    ProjectUpdate,
)
def _ensure_can_modify(
    project: Project,
    user: User,
    action: str = "thao tác với",
) -> None:
    """Admin quản lý mọi project, manager chỉ quản lý project mình sở hữu."""
    if user.role == ADMIN:
        return

    if user.role == MANAGER and project.owner_id == user.id:
        return

    raise ForbiddenError(
        f"Bạn không có quyền {action} project do người khác sở hữu",
        code="PROJECT_FORBIDDEN",
    )


def _escape_like(text: str) -> str:
    """Escape ký tự đặc biệt của LIKE để % và _ được hiểu là ký tự thường."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _ensure_owner_exists(db: Session, owner_id: Optional[uuid.UUID]) -> None:
    if owner_id is not None and db.get(User, owner_id) is None:
        raise BadRequestError("owner_id không tồn tại", code="OWNER_NOT_FOUND")

def list_projects(
    db: Session,
    search: Optional[str] = None,
    owner_id: Optional[uuid.UUID] = None,
    created_after: Optional[date] = None,
    created_before: Optional[date] = None,
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> dict:
    # Chốt chặn cho trường hợp gọi từ nơi không qua validation của router
    skip = max(skip, 0)
    limit = min(max(limit, 1), MAX_LIMIT)
    """func.unaccent(...)	Bỏ dấu trong chuỗi"""

    filters = []
    if search and search.strip():
        pattern = f"%{_escape_like(search.strip())}%"
        filters.append(
            or_(
                func.unaccent(Project.name).ilike( 
                    func.unaccent(pattern), escape="\\" 
                ),
                func.unaccent(Project.description).ilike(
                    func.unaccent(pattern), escape="\\"
                ),
            )
        )
    if owner_id is not None:
        filters.append(Project.owner_id == owner_id)
    if created_after:
        filters.append(
            Project.created_at >= datetime.combine(created_after, time.min)
        )
    if created_before:
        # Tính đến hết ngày được chọn
        end = datetime.combine(created_before + timedelta(days=1), time.min)
        filters.append(Project.created_at < end)

    total = db.scalar(select(func.count()).select_from(Project).where(*filters)) or 0

    # Không có dữ liệu hoặc skip vượt quá tổng: bỏ qua query lấy dữ liệu
    if total == 0 or skip >= total:
        return {"items": [], "total": total, "skip": skip, "limit": limit, "has_more": False}

    items = db.scalars(
        select(Project)
        .where(*filters)
        .order_by(Project.created_at.desc(), Project.id.desc())  # id làm tiebreaker
        .offset(skip)
        .limit(limit)
    ).all()

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + len(items) < total,
    }


def get_project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise NotFoundError("Project không tồn tại", code="PROJECT_NOT_FOUND")
    return project



def create_project(db: Session, payload: ProjectCreate, user: User) -> Project:
    project = Project(**payload.model_dump(), owner_id=user.id)
    db.add(project)
    db.flush()  # lấy project.id

    # Owner tự động là thành viên, để chọn được làm assignee
    db.add(ProjectMember(project_id=project.id, user_id=user.id))
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session, project_id: int, payload: ProjectUpdate, user: User
) -> Project:
    project = get_project(db, project_id)  # 404 trước
    _ensure_can_modify(project, user, "chỉnh sửa")  # rồi 403

    update_data = payload.model_dump(exclude_unset=True)

    if "owner_id" in update_data:
        if user.role != ADMIN:
            raise ForbiddenError(
                "Chỉ admin mới được đổi chủ sở hữu project",
                code="PROJECT_OWNER_CHANGE_FORBIDDEN",
            )
        _ensure_owner_exists(db, update_data["owner_id"])

    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, user: User) -> None:
    project = get_project(db, project_id)  # 404 trước
    _ensure_can_modify(project, user, "xóa")      # admin, hoặc manager là chủ
    db.delete(project)
    db.commit()