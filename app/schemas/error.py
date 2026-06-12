from pydantic import BaseModel


class FieldError(BaseModel):
    field: str
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ValidationErrorResponse(BaseModel):
    code: str
    message: str
    errors: list[FieldError]
