from fastapi import status


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    def __init__(self, message: str, details: dict | None = None):
        from app.core.error_codes import ErrorCode
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str, code: str | None = None):
        from app.core.error_codes import ErrorCode
        super().__init__(
            code=code or ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str, code: str | None = None):
        from app.core.error_codes import ErrorCode
        super().__init__(
            code=code or ErrorCode.FORBIDDEN,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(AppException):
    def __init__(self, message: str, code: str | None = None):
        from app.core.error_codes import ErrorCode
        super().__init__(
            code=code or ErrorCode.NOT_FOUND,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictException(AppException):
    def __init__(self, message: str, code: str | None = None):
        from app.core.error_codes import ErrorCode
        super().__init__(
            code=code or ErrorCode.CONFLICT,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class InternalServerException(AppException):
    def __init__(self, message: str = "Internal server error", code: str | None = None):
        from app.core.error_codes import ErrorCode
        super().__init__(
            code=code or ErrorCode.INTERNAL_SERVER_ERROR,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
