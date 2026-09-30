from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.router import router
from app.db.session import SessionLocal


def _request_id(request: Request) -> str:
    incoming = request.headers.get("X-Request-ID")
    if incoming:
        try:
            return str(uuid.UUID(incoming))
        except ValueError:
            pass
    return str(uuid.uuid4())


def _error_code(status_code: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
    }.get(status_code, "HTTP_ERROR")


def create_app() -> FastAPI:
    app = FastAPI(title="Ops Intelligence API", version="0.2.0")

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = _request_id(request)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": _error_code(exc.status_code),
                    "message": str(exc.detail),
                    "details": None,
                    "request_id": request.state.request_id,
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "request_id": request.state.request_id,
                }
            },
        )

    app.include_router(router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}

    return app


app = create_app()
