class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"  # Default code for each error type

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code  # Allow overriding the code when raising an exception


class BadRequestError(AppError):
    status_code = 400  # The request is invalid
    code = "BAD_REQUEST"  # Error code for an invalid request


class UnauthorizedError(AppError):
    status_code = 401  # Authentication is missing or invalid
    code = "UNAUTHORIZED"  # Error code for unauthenticated requests


class ForbiddenError(AppError):
    status_code = 403  # The user is authenticated but lacks permission to perform the action
    code = "FORBIDDEN"  # Error code for access denial


class NotFoundError(AppError):
    status_code = 404  # The requested resource was not found
    code = "NOT_FOUND"  # Error code for a resource that was not found


class ConflictError(AppError):
    status_code = 409  # The data or resource state conflicts with the request
    code = "CONFLICT"  # Error code for a data conflict


class InternalServerError(AppError):
    status_code = 500  # The server encountered an unexpected error
    code = "INTERNAL_SERVER_ERROR"  # Error code for an internal server error


class ContentMissingError(AppError):
    status_code = 500  # Required content is missing to process the request (the exact error nature should be determined)
    code = "CONTENT_MISSING"  # Error code for missing content


class StoreUnavailableError(AppError):
    status_code = 503  # The storage service is temporarily unavailable
    code = "STORE_UNAVAILABLE"  # Error code for an unavailable storage service
