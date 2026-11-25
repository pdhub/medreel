import pytest
from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)
UNKNOWN = "00000000-0000-4000-8000-000000000000"


def new_job():
    r = client.post("/api/jobs")
    assert r.status_code == 201 and r.json()["status"] == "created"
    return r.json()["job_id"]


def upload(job_id, path, name=None, content_type="video/mp4"):
    with open(path, "rb") as f:
        return client.post(f"/api/jobs/{job_id}/upload", files={"file": (name or path.name, f, content_type)})


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_unknown_job_uses_error_shape():
    r = client.get(f"/api/jobs/{UNKNOWN}")
    assert r.status_code == 404
    assert r.json() == {"error": {"code": "job_not_found", "message": "no job with this id", "job_id": UNKNOWN}}


def test_bad_uuid_is_422():
    r = client.get("/api/jobs/not-a-uuid")
    assert r.status_code == 422 and r.json()["error"]["code"] == "validation_error"


def test_upload_start_flow(make_video):
    job_id = new_job()
    assert client.post(f"/api/jobs/{job_id}/start").status_code == 409  # not uploaded yet
    r = upload(job_id, make_video())
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "uploaded"
    r = client.post(f"/api/jobs/{job_id}/start")
    assert r.status_code == 202 and r.json()["status"] == "queued"
    assert client.get(f"/api/jobs/{job_id}/output").status_code == 409
    assert client.get(f"/api/jobs/{job_id}/transcript").json()["error"]["code"] == "not_ready"


@pytest.mark.parametrize("kind, code", [("extension", 415), ("content_type", 415), ("not_video", 415),
                                         ("no_audio", 415), ("missing", 422)])
def test_upload_validation(make_video, tmp_path, kind, code):
    job_id = new_job()
    if kind == "extension":
        r = upload(job_id, make_video(), name="clip.mov")
    elif kind == "content_type":
        r = upload(job_id, make_video(), content_type="text/plain")
    elif kind == "not_video":
        fake = tmp_path / "fake.mp4"
        fake.write_bytes(b"not a video")
        r = upload(job_id, fake)
    elif kind == "no_audio":
        r = upload(job_id, make_video(audio=False))
    else:
        r = client.post(f"/api/jobs/{job_id}/upload", data={"other": "x"})
    assert r.status_code == code, r.text
    assert client.get(f"/api/jobs/{job_id}").json()["status"] == "created"


def test_upload_too_large(make_video, monkeypatch):
    from services.config import settings
    monkeypatch.setattr(settings, "max_upload_mb", 0)
    r = upload(new_job(), make_video())
    assert r.status_code == 413 and r.json()["error"]["code"] == "file_too_large"
