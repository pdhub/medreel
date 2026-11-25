import logging
import shutil
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from starlette.datastructures import UploadFile

from agents.editing_planner.planner import EditPlan
from apps.api.schemas.jobs import ErrorResponse, Job, JobCreated, Transcript
from services.config import settings
from services.ffmpeg.media import MediaError, inspect_upload
from services.jobs.store import InvalidTransition, JobStore
from services.storage.backend import LocalStorage, get_json, put_json

log = logging.getLogger("medreel.api")
store = JobStore(settings.data_dir / "jobs.db")
storage = LocalStorage(settings.data_dir / "storage")
router = APIRouter(prefix="/api/jobs", responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse},
                                                  422: {"model": ErrorResponse}})


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, job_id: str | None = None):
        super().__init__(message)
        self.status, self.code, self.message, self.job_id = status, code, message, job_id


def _job(row: dict) -> Job:
    return Job(job_id=row["id"], status=row["status"], error=row["error"], created_at=row["created_at"],
               updated_at=row["updated_at"])


def _artifact(job_id: str, name: str):
    store.get(job_id)
    key = f"{job_id}/{name}"
    if not storage.exists(key):
        raise ApiError(409, "not_ready", f"{name} is not available yet", job_id)
    return get_json(storage, key)


@router.post("", response_model=JobCreated, status_code=201)
def create_job():
    row = store.create()
    log.info("job created", extra={"job_id": row["id"]})
    return JobCreated(job_id=row["id"], status=row["status"])


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: UUID):
    return _job(store.get(str(job_id)))


def _save_upload(job_id: str, upload: UploadFile) -> None:
    tmp = settings.data_dir / "tmp" / f"{job_id}.upload.mp4"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(tmp, "wb") as f:
            shutil.copyfileobj(upload.file, f)
        meta = inspect_upload(tmp)
        with open(tmp, "rb") as f:
            storage.put(f"{job_id}/source.mp4", f)
        put_json(storage, f"{job_id}/source.json", meta)
    finally:
        tmp.unlink(missing_ok=True)


@router.post("/{job_id}/upload", response_model=Job,
             responses={413: {"model": ErrorResponse}, 415: {"model": ErrorResponse}})
async def upload_video(job_id: UUID, request: Request):
    """Multipart upload, field "file". shortcut: the body passes through the API; switch to signed R2 uploads
    (see R2Storage) before accepting large real-world files."""
    jid, limit = str(job_id), settings.max_upload_mb * 1024 * 1024
    status = store.get(jid)["status"]
    if status not in ("created", "uploaded"):
        raise InvalidTransition(jid, status, "uploaded")
    if int(request.headers.get("content-length") or 0) > limit + 1024 * 1024:  # allow for multipart overhead
        raise ApiError(413, "file_too_large", f"uploads are limited to {settings.max_upload_mb} MB", jid)
    form = await request.form()
    try:
        upload = form.get("file")
        if not isinstance(upload, UploadFile):
            raise ApiError(422, "missing_file", 'send the video as the multipart field "file"', jid)
        if not (upload.filename or "").lower().endswith(".mp4"):
            raise ApiError(415, "unsupported_format", "only .mp4 files are supported", jid)
        if upload.content_type not in ("video/mp4", "application/octet-stream"):
            raise ApiError(415, "unsupported_format", f"content type {upload.content_type} is not video/mp4", jid)
        if (upload.size or 0) > limit:
            raise ApiError(413, "file_too_large", f"uploads are limited to {settings.max_upload_mb} MB", jid)
        try:
            await run_in_threadpool(_save_upload, jid, upload)
        except MediaError as e:
            raise ApiError(415, "unsupported_format", str(e), jid) from None
    finally:
        await form.close()
    row = store.transition(jid, "uploaded")
    log.info("video uploaded", extra={"job_id": jid, "status": row["status"]})
    return _job(row)


@router.post("/{job_id}/start", response_model=Job, status_code=202)
def start_job(job_id: UUID):
    row = store.transition(str(job_id), "queued")
    log.info("job queued", extra={"job_id": row["id"], "status": row["status"]})
    return _job(row)


@router.get("/{job_id}/transcript", response_model=Transcript)
def get_transcript(job_id: UUID):
    return _artifact(str(job_id), "transcript.json")


@router.get("/{job_id}/editing-plan", response_model=EditPlan)
def get_editing_plan(job_id: UUID):
    return _artifact(str(job_id), "plan.json")


@router.get("/{job_id}/output", response_class=FileResponse)
def get_output(job_id: UUID):
    jid = str(job_id)
    if store.get(jid)["status"] != "done":
        raise ApiError(409, "not_ready", "the edited video is not ready yet", jid)
    return FileResponse(storage.get(f"{jid}/output.mp4"), media_type="video/mp4", filename=f"{jid}.mp4")
