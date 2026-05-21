import logging
import os
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import Base, engine
from .routes import router

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("notification-service")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification Service",
    description="Notification service for task events",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_response(code: str, message: str, details=None):
    return {"code": code, "message": message, "details": details}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        "%s %s -> %s (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Process-Time-ms"] = str(duration_ms)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response("HTTP_ERROR", str(exc.detail), None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(
            "VALIDATION_ERROR",
            "Request validation failed",
            exc.errors(),
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error during %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=error_response("INTERNAL_SERVER_ERROR", "Unexpected server error", None),
    )


app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "Notification Service",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "notification-service",
    }
