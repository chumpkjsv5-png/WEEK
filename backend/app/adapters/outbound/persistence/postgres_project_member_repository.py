from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.domain.errors import MemberAlreadyExists
from app.domain.project import Project
from app.domain.project_member import Member, MemberUser
from app.domain.task import TaskStatus
from app.models.project_data import Project as ProjectRow
from app.models.project_member import ProjectMember
from app.models.task_data import Task as TaskRow
from app.models.user_data import User


def _to_member(row: ProjectMember) -> Member:
    return Member(
        project_id=row.project_id,
        user_id=row.user_id,
        created_at=row.created_at,
        user=MemberUser(
            id=row.user.id, full_name=row.user.full_name, email=row.user.email
        ),
    )


class PostgresProjectMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_project(self, project_id: int) -> Optional[Project]:
        row = self.db.get(ProjectRow, project_id)
        if row is None:
            return None
        return Project(
            id=row.id,
            name=row.name,
            description=row.description,
            owner_id=row.owner_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def list_members(self, project_id: int) -> list[Member]:
        stmt = (
            select(ProjectMember)
            .options(joinedload(ProjectMember.user))  # lấy luôn user, tránh query lặp
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.created_at)
        )
        return [_to_member(r) for r in self.db.scalars(stmt).all()]

    def search_candidates(
        self, project_id: int, q: str, limit: int
    ) -> list[MemberUser]:
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
        return [
            MemberUser(id=u.id, full_name=u.full_name, email=u.email)
            for u in self.db.scalars(stmt).all()
        ]

    def user_exists(self, user_id: UUID) -> bool:
        return self.db.get(User, user_id) is not None

    def get_member(self, project_id: int, user_id: UUID) -> Optional[Member]:
        row = self.db.get(ProjectMember, (project_id, user_id))
        return _to_member(row) if row else None

    def add(self, project_id: int, user_id: UUID) -> Member:
        row = ProjectMember(project_id=project_id, user_id=user_id)
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError:  # phòng hai request thêm cùng lúc
            self.db.rollback()
            raise MemberAlreadyExists("User đã là thành viên của project")
        self.db.refresh(row)
        return _to_member(row)

    def remove(self, project_id: int, user_id: UUID) -> None:
        row = self.db.get(ProjectMember, (project_id, user_id))
        if row is not None:
            self.db.delete(row)
            self.db.commit()

    def count_open_tasks(self, project_id: int, user_id: UUID) -> int:
        return self.db.scalar(
            select(func.count())
            .select_from(TaskRow)
            .where(
                TaskRow.project_id == project_id,
                TaskRow.assignee_id == user_id,
                TaskRow.status != TaskStatus.COMPLETED,
            )
        ) or 0