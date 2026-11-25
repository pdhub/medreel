import pytest

from services.jobs.store import InvalidTransition, JobNotFound, JobStore


@pytest.fixture
def store(tmp_path):
    return JobStore(tmp_path / "jobs.db")


def test_happy_path(store):
    job = store.create()
    assert job["status"] == "created"
    for status in ("uploaded", "queued"):
        store.transition(job["id"], status)
    assert store.claim_next() == job["id"]
    assert store.claim_next() is None  # claimed once only
    for status in ("planning", "rendering", "done"):
        store.transition(job["id"], status)
    assert store.get(job["id"])["status"] == "done"


def test_start_before_upload_is_rejected(store):
    job = store.create()
    with pytest.raises(InvalidTransition) as e:
        store.transition(job["id"], "queued")
    assert e.value.current == "created"


def test_failed_job_can_be_requeued_and_error_clears(store):
    job = store.create()
    store.transition(job["id"], "uploaded")
    store.transition(job["id"], "queued")
    store.transition(job["id"], "failed", error="boom")
    assert store.get(job["id"])["error"] == "boom"
    assert store.transition(job["id"], "queued")["error"] is None


def test_unknown_job(store):
    with pytest.raises(JobNotFound):
        store.transition("00000000-0000-0000-0000-000000000000", "queued")
