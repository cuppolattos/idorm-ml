from fastapi import FastAPI
from app.router import router
from app.model_loader import model_loader
from fastapi import Request
from fastapi.responses import JSONResponse, Response
import traceback
import logging
from fastapi import HTTPException
from app.middleware import RequestIDMiddleware
import json
from app.logging_config import setup_logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from prometheus_fastapi_instrumentator import Instrumentator

setup_logging()

app = FastAPI(title="Kos Price Prediction API")

Instrumentator().instrument(app).expose(app)

app.include_router(router)
app.add_middleware(RequestIDMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    logger = logging.getLogger("error")

    logger.error(
        "unhandled_exception",
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "error": str(exc),
            "request_id": getattr(request.state, "request_id", None)
        }
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        },
    )

@app.on_event("startup")
def startup_event():
    model_loader.load_models()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):

    logger = logging.getLogger("error")

    logger.warning(
        "http_exception",
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "fail",
            "message": exc.detail
        },
    )