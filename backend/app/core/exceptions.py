class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"  # mã mặc định của từng loại lỗi

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code  # cho phép ghi đè code khi raise


class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"


class InternalServerError(AppError):
    status_code = 500
    code = "INTERNAL_SERVER_ERROR"

class ContentMissingError(AppError):          # đổi AppError cho đúng tên lớp cha của bạn
    status_code = 500
    code = "CONTENT_MISSING"


class StoreUnavailableError(AppError):
    status_code = 503
    code = "STORE_UNAVAILABLE"