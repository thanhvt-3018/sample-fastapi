class ErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_INACTIVE = "USER_INACTIVE"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_REVOKED = "TOKEN_REVOKED"

    INVALID_PASSWORD = "INVALID_PASSWORD"
    WEAK_PASSWORD = "WEAK_PASSWORD"

    WORKSPACE_NOT_FOUND = "WORKSPACE_NOT_FOUND"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    MEMBER_NOT_FOUND = "MEMBER_NOT_FOUND"
    MEMBER_ALREADY_EXISTS = "MEMBER_ALREADY_EXISTS"
    NOT_WORKSPACE_OWNER = "NOT_WORKSPACE_OWNER"
    NOT_PROJECT_OWNER = "NOT_PROJECT_OWNER"
    CANNOT_REMOVE_OWNER = "CANNOT_REMOVE_OWNER"


ERROR_MESSAGES = {
    ErrorCode.VALIDATION_ERROR: "Validation error occurred",
    ErrorCode.UNAUTHORIZED: "Unauthorized access",
    ErrorCode.FORBIDDEN: "Access forbidden",
    ErrorCode.NOT_FOUND: "Resource not found",
    ErrorCode.CONFLICT: "Resource already exists",
    ErrorCode.UNPROCESSABLE_ENTITY: "Unprocessable entity",
    ErrorCode.INTERNAL_SERVER_ERROR: "Internal server error",

    ErrorCode.INVALID_CREDENTIALS: "Invalid email or password",
    ErrorCode.USER_NOT_FOUND: "User not found",
    ErrorCode.USER_ALREADY_EXISTS: "User with this email already exists",
    ErrorCode.USER_INACTIVE: "User account is inactive",
    ErrorCode.INSUFFICIENT_PERMISSIONS: "Insufficient permissions for this action",

    ErrorCode.INVALID_TOKEN: "Invalid or malformed token",
    ErrorCode.TOKEN_EXPIRED: "Token has expired",
    ErrorCode.TOKEN_REVOKED: "Token has been revoked",

    ErrorCode.INVALID_PASSWORD: "Invalid current password",
    ErrorCode.WEAK_PASSWORD: "Password does not meet security requirements",

    ErrorCode.WORKSPACE_NOT_FOUND: "Workspace not found",
    ErrorCode.PROJECT_NOT_FOUND: "Project not found",
    ErrorCode.MEMBER_NOT_FOUND: "Member not found in workspace",
    ErrorCode.MEMBER_ALREADY_EXISTS: "User is already a member of this workspace",
    ErrorCode.NOT_WORKSPACE_OWNER: "Only workspace owner can perform this action",
    ErrorCode.NOT_PROJECT_OWNER: "Only project owner can perform this action",
    ErrorCode.CANNOT_REMOVE_OWNER: "Cannot remove workspace owner",
}
