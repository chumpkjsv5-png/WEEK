from app.database import SessionLocal
from app.models.user_data import User
from app.models.project_data import Project            # noqa: F401
from app.models.task_data import Task                  # noqa: F401
from app.models.project_member import ProjectMember  # noqa: F401
from app.core.security import hash_password


def main() -> None:
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.password_hash == "!").all()
        for u in users:
            u.password_hash = hash_password("ChangeMe123!")
        db.commit()
        print(f"Updated {len(users)} user(s)")
    finally:
        db.close()


if __name__ == "__main__":
    main()