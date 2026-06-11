from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies.auth import (
    get_current_active_user,
    get_refresh_token_from_cookie,
    oauth2_scheme,
)
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> Response:
    tokens = await AuthService(session).register(data)

    response = JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "access_token": tokens["access_token"],
            "token_type": "bearer",
        },
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return response


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> Response:
    tokens = await AuthService(session).login(data)

    response = JSONResponse(
        content={
            "access_token": tokens["access_token"],
            "token_type": "bearer",
        },
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    _: RefreshRequest = Depends(),  # Just for documentation
    refresh_token: str = Depends(get_refresh_token_from_cookie),
    session: AsyncSession = Depends(get_db),
) -> Response:
    tokens = await AuthService(session).refresh(refresh_token)

    response = JSONResponse(
        content={
            "access_token": tokens["access_token"],
            "token_type": "bearer",
        },
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_active_user),
    access_token: str = Depends(oauth2_scheme),
    refresh_token: str = Depends(get_refresh_token_from_cookie),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await AuthService(session).logout(
        user_id=current_user.id,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return response
