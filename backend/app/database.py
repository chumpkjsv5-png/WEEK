import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load biến môi trường từ file .env
load_dotenv()

# Lấy connection string từ .env, có fallback mặc định (chỉnh lại theo máy bạn)
DATABASE_URL = os.getenv("DATABASE_URL")


# Tạo engine kết nối tới PostgreSQL
engine = create_engine(DATABASE_URL)

# Session factory - mỗi request sẽ tạo 1 session riêng
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class để các model kế thừa (Task, User, ...)
Base = declarative_base()


# Dependency dùng trong FastAPI (Depends(get_db))
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()