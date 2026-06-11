from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response with access token only. Refresh token is set as HttpOnly cookie."""
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Empty request - refresh token comes from HttpOnly cookie."""
    pass
