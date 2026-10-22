from datetime import datetime, time, timedelta
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.errors import ProjectNotFound
from app.domain.project import NewProject, Project, ProjectFilter
from app.models.project_data import Project as ProjectRow
from app.models.project_member import ProjectMember
from app.models.user_data import User

_UPDATABLE = {"name", "description", "owner_id"}


def _escape_like(text: str) -> str:
    """Escape ký tự đặc biệt của LIKE để % và _ được hiểu là ký tự thường."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _to_domain(row: ProjectRow) -> Project:
    return Project(
        id=row.id,
        name=row.name,
        description=row.description,
        owner_id=row.owner_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def user_exists(self, user_id: UUID) -> bool:
        return self.db.get(User, user_id) is not None

    def get(self, project_id: int) -> Optional[Project]:
        row = self.db.get(ProjectRow, project_id)
        return _to_domain(row) if row else None

    def add_with_owner_member(self, new: NewProject) -> Project:
        try:
            row = ProjectRow(
                name=new.name, description=new.description, owner_id=new.owner_id
            )
            self.db.add(row)
            self.db.flush()  # lấy row.id
            # Owner tự động là thành viên, để chọn được làm assignee
            self.db.add(ProjectMember(project_id=row.id, user_id=new.owner_id))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(row)
        return _to_domain(row)

    def update(self, project_id: int, changes: dict[str, Any]) -> Project:
        row = self.db.get(ProjectRow, project_id)
        if row is None:
            raise ProjectNotFound("Project không tồn tại")
        for key, value in changes.items():
            if key in _UPDATABLE:
                setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return _to_domain(row)

    def delete(self, project_id: int) -> None:
        row = self.db.get(ProjectRow, project_id)
        if row is not None:
            self.db.delete(row)
            self.db.commit()

    def search(self, f: ProjectFilter) -> tuple[list[Project], int]:
        filters = []
        if f.search and f.search.strip():
            pattern = f"%{_escape_like(f.search.strip())}%"
            filters.append(
                or_(
                    func.unaccent(ProjectRow.name).ilike(
                        func.unaccent(pattern), escape="\\"
                    ),
                    func.unaccent(ProjectRow.description).ilike(
                        func.unaccent(pattern), escape="\\"
                    ),
                )
            )
        if f.owner_id is not None:
            filters.append(ProjectRow.owner_id == f.owner_id)
        if f.created_after:
            filters.append(
                ProjectRow.created_at >= datetime.combine(f.created_after, time.min)
            )
        if f.created_before:
            # Tính đến hết ngày được chọn
            end = datetime.combine(f.created_before + timedelta(days=1), time.min)
            filters.append(ProjectRow.created_at < end)

        total = self.db.scalar(
            select(func.count()).select_from(ProjectRow).where(*filters)
        ) or 0

        # Không có dữ liệu hoặc skip vượt quá tổng: bỏ qua query lấy dữ liệu
        if total == 0 or f.skip >= total:
            return [], total

        rows = self.db.scalars(
            select(ProjectRow)
            .where(*filters)
            .order_by(ProjectRow.created_at.desc(), ProjectRow.id.desc())  # id làm tiebreaker
            .offset(f.skip)
            .limit(f.limit)
        ).all()
        return [_to_domain(r) for r in rows], total