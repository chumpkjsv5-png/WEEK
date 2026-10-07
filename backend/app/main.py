from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

# # Import model để SQLAlchemy nhận biết bảng
# from app.models.task_data import Task

# Import router
from app.routers import task_router, project_router, user_router, project_members_router


app = FastAPI(
    title="Week Task API",
    description="Task Management API - React + FastAPI + PostgreSQL",
    version="1.0.0",
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Database
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# Routes
# =========================

@app.get("/")
def root():
    return {
        "message": "Week 1 Task API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


# Include router Task
app.include_router(task_router.router)
app.include_router(project_router.router)
app.include_router(user_router.router)
app.include_router(project_members_router.router)