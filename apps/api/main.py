import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from apps.api.routes.jobs import ApiError, router
from apps.api.schemas.jobs import Health
from services.config import settings
from services.jobs.store import InvalidTransition, JobNotFound
from services.log import setup_logging

setup_logging(settings.log_level)
log = logging.getLogger("medreel.api")
app = FastAPI(title="MedReel API", version="0.1.0")


def _error(status: int, code: str, message: str, job_id: str | None = None) -> JSONResponse:
    body = {"code": code, "message": message} | ({"job_id": job_id} if job_id else {})
    return JSONResponse(status_code=status, content={"error": body})


@app.exception_handler(ApiError)
def api_error(_, e: ApiError):
    return _error(e.status, e.code, e.message, e.job_id)


@app.exception_handler(JobNotFound)
def not_found(_, e: JobNotFound):
    return _error(404, "job_not_found", "no job with this id", e.job_id)


@app.exception_handler(InvalidTransition)
def invalid_state(_, e: InvalidTransition):
    return _error(409, "invalid_state", str(e), e.job_id)


@app.exception_handler(RequestValidationError)
def validation_error(_, e: RequestValidationError):
    fields = "; ".join(f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors())
    return _error(422, "validation_error", fields)


@app.exception_handler(HTTPException)
def http_error(_, e: HTTPException):
    return _error(e.status_code, "http_error", str(e.detail))


@app.middleware("http")
async def access_log(request: Request, call_next):
    started = time.monotonic()
    response = await call_next(request)
    log.info("request", extra={"method": request.method, "path": request.url.path, "status_code": response.status_code,
                               "duration_s": round(time.monotonic() - started, 3)})
    return response


@app.get("/health", response_model=Health)
def health():
    return Health(status="ok")


app.include_router(router)
