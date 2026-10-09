
class AppError(Exception):
    status_code = 400  # Lỗi cơ sở, mặc định là Bad Request

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class BadRequestError(AppError):
    status_code = 400  # Yêu cầu không hợp lệ (dữ liệu sai)


class UnauthorizedError(AppError):
    status_code = 401  # Chưa đăng nhập hoặc xác thực thất bại


class ForbiddenError(AppError):
    status_code = 403  # Đã đăng nhập nhưng không có quyền


class NotFoundError(AppError):
    status_code = 404  # Không tìm thấy tài nguyên


class ConflictError(AppError):
    status_code = 409  # Xung đột dữ liệu hoặc trạng thái


class InternalServerError(AppError):
    status_code = 500  # Lỗi nội bộ máy chủ
