from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


from app.database import Base, engine

# # Import model để SQLAlchemy nhận biết bảng
# from app.models.task_data import Task

# Import router
from app.adapters.inbound.http.article_router import router as article_router
from app.adapters.inbound.http.task_router import router as task_router
from app.adapters.inbound.http.project_router import router as project_router
from app.adapters.inbound.http.project_members_router import router as project_members_router
from app.adapters.inbound.http.user_router import router as user_router
from app.adapters.inbound.http.auth_router import router as auth_router

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppError



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

@app.get("/boom")
def boom():
    raise RuntimeError("secret detail")

logger = logging.getLogger(__name__)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": {"code": exc.code, "message": exc.message}},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Stack trace chỉ ghi vào log server, không trả ra client
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Đã xảy ra lỗi hệ thống",
            }
        },
    )

# Include router Task
app.include_router(task_router)
app.include_router(project_router)
app.include_router(user_router)
app.include_router(project_members_router)
app.include_router(auth_router)
app.include_router(article_router)