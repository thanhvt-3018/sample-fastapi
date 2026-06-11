from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.error_codes import ErrorCode, ERROR_MESSAGES
from app.core.exceptions import AppException
from app.core.redis import close_redis, init_redis
from app.schemas.error import ErrorResponse, FieldError, ValidationErrorResponse

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up %s v%s", settings.APP_NAME, settings.APP_VERSION)
    await init_redis()
    yield
    await engine.dispose()
    await close_redis()
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.code,
                message=exc.message,
                details=exc.details if exc.details else None,
            ).model_dump(exclude_none=True),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code = (
            ErrorCode.NOT_FOUND if exc.status_code == status.HTTP_404_NOT_FOUND
            else ErrorCode.FORBIDDEN if exc.status_code == status.HTTP_403_FORBIDDEN
            else ErrorCode.UNAUTHORIZED if exc.status_code == status.HTTP_401_UNAUTHORIZED
            else ErrorCode.INTERNAL_SERVER_ERROR
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(code=code, message=str(
                exc.detail)).model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", [])[1:])
            message = error.get("msg", "Invalid value")
            error_type = error.get("type", "")

            errors.append(
                FieldError(
                    field=field or "unknown",
                    message=message,
                    code=error_type,
                )
            )

        response = ValidationErrorResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message=ERROR_MESSAGES[ErrorCode.VALIDATION_ERROR],
            errors=errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                message=ERROR_MESSAGES[ErrorCode.INTERNAL_SERVER_ERROR],
            ).model_dump(exclude_none=True),
        )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Health"])
    def health_check() -> dict:
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()
