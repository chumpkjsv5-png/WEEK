    # app/services/project_member_service.py
    from sqlalchemy import func, or_, select
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Session, joinedload

    from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
    from app.models.project_data import Project
    from app.models.project_member import ProjectMember
    from app.models.task_data import Task
    from app.models.user_data import User
    from app.schemas.task_schema import TaskStatus
    from app.core.permissions import ADMIN, MANAGER


    def _ensure_can_manage_members(project: Project, user: User) -> None:
        """Admin quản lý mọi project, manager chỉ project mình sở hữu."""
        if user.role == ADMIN:
            return
        if user.role == MANAGER and project.owner_id == user.id:
            return
        raise ForbiddenError(
            "Bạn chỉ được quản lý thành viên của project do mình sở hữu",
            code="PROJECT_MEMBER_FORBIDDEN",
        )


    def _get_project(db: Session, project_id: int) -> Project:
        project = db.get(Project, project_id)
        if not project:
            raise NotFoundError("Project không tồn tại", code="PROJECT_NOT_FOUND")
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


    def search_users_to_add(db: Session, project_id: int, q: str, user: User, limit: int =10):
        """Tìm user theo tên/email để thêm vào project.Loại các user đã là thành viên của project."""
        project = _get_project(db, project_id)
        _ensure_can_manage_members(project, user)
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


    def add_member(db: Session, project_id: int, user_id, user: User):
        project = _get_project(db, project_id)
        _ensure_can_manage_members(project, user)
        if not db.get(User, user_id):
            raise NotFoundError("User không tồn tại", code="USER_NOT_FOUND")
        if db.get(ProjectMember, (project_id, user_id)):
            raise ConflictError(
                "User đã là thành viên của project",
                code="MEMBER_ALREADY_EXISTS",
            )

        member = ProjectMember(project_id=project_id, user_id=user_id)
        db.add(member)
        try:
            db.commit()
        except IntegrityError:  # phòng hai request thêm cùng lúc
            db.rollback()
            raise ConflictError(
                "User đã là thành viên của project",
                code="MEMBER_ALREADY_EXISTS",
            )
        db.refresh(member)
        return member


    def remove_member(db: Session, project_id: int, user_id, user: User) -> None:
        project = _get_project(db, project_id)
        _ensure_can_manage_members(project, user)
        if project.owner_id == user_id:
            raise ConflictError(
                "Không thể gỡ chủ sở hữu khỏi project",
                code="CANNOT_REMOVE_OWNER",
            )

        member = db.get(ProjectMember, (project_id, user_id))
        if not member:
            raise NotFoundError(
                "User không phải thành viên của project",
                code="MEMBER_NOT_FOUND",
            )

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
                "hãy hoàn thành hoặc giao lại trước khi gỡ",
                code="MEMBER_HAS_OPEN_TASKS",
            )

        db.delete(member)
        db.commit()