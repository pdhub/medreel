from datetime import datetime
from typing import Literal

from pydantic import BaseModel

JobStatus = Literal["created", "uploaded", "queued", "transcribing", "planning", "rendering", "done", "failed"]


class Health(BaseModel):
    status: Literal["ok"]


class JobCreated(BaseModel):
    job_id: str
    status: JobStatus


class Job(BaseModel):
    job_id: str
    status: JobStatus
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class Word(BaseModel):
    text: str
    start: float
    end: float
    probability: float | None = None


class Transcript(BaseModel):
    language: str | None
    duration: float
    words: list[Word]


class ErrorBody(BaseModel):
    code: str
    message: str
    job_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody
