from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserOut      # thêm dòng này
from app.database import get_db           # đổi đường dẫn cho khớp project của bạn

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT id, email, full_name FROM users ORDER BY full_name")
    ).mappings().all()
    return rows