class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"  # mã mặc định của từng loại lỗi

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code  # cho phép ghi đè code khi raise


class BadRequestError(AppError):
    status_code = 400  # Yêu cầu không hợp lệ
    code = "BAD_REQUEST"  # Mã lỗi yêu cầu không hợp lệ


class UnauthorizedError(AppError):
    status_code = 401  # Chưa xác thực hoặc thông tin xác thực không hợp lệ
    code = "UNAUTHORIZED"  # Mã lỗi chưa xác thực


class ForbiddenError(AppError):
    status_code = 403  # Đã xác thực nhưng không có quyền thực hiện thao tác
    code = "FORBIDDEN"  # Mã lỗi không có quyền truy cập


class NotFoundError(AppError):
    status_code = 404  # Không tìm thấy tài nguyên được yêu cầu
    code = "NOT_FOUND"  # Mã lỗi không tìm thấy tài nguyên


class ConflictError(AppError):
    status_code = 409  # Dữ liệu hoặc trạng thái bị xung đột
    code = "CONFLICT"  # Mã lỗi xung đột dữ liệu


class InternalServerError(AppError):
    status_code = 500  # Máy chủ gặp lỗi không mong muốn
    code = "INTERNAL_SERVER_ERROR"  # Mã lỗi máy chủ nội bộ


class ContentMissingError(AppError):
    status_code = 500  # Thiếu nội dung cần thiết để xử lý yêu cầu (cần xác định đúng bản chất lỗi)
    code = "CONTENT_MISSING"  # Mã lỗi thiếu nội dung


class StoreUnavailableError(AppError):
    status_code = 503  # Dịch vụ lưu trữ tạm thời không khả dụng
    code = "STORE_UNAVAILABLE"  # Mã lỗi dịch vụ lưu trữ không khả dụng