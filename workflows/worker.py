"""Separate worker process: claims queued jobs and runs the production graph. Video is never processed in the API."""
import logging
import time

from agents.editing_planner.planner import get_planner
from services.config import settings
from services.jobs.store import JobStore
from services.log import setup_logging
from services.storage.backend import LocalStorage
from services.transcription.whisper import FasterWhisperTranscriber
from workflows.production_graph import build_graph

log = logging.getLogger("medreel.worker")


def main():
    setup_logging(settings.log_level)
    store = JobStore(settings.data_dir / "jobs.db")
    tmp_dir = settings.data_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    planner = get_planner(settings.anthropic_api_key, settings.anthropic_model)
    graph = build_graph(store, LocalStorage(settings.data_dir / "storage"),
                        FasterWhisperTranscriber(settings.whisper_model, settings.whisper_compute_type),
                        planner, tmp_dir)
    log.info("worker started", extra={"planner": type(planner).__name__})
    while True:
        job_id = store.claim_next()
        if job_id is None:
            time.sleep(settings.worker_poll_seconds)
            continue
        try:
            graph.invoke({"job_id": job_id})
            log.info("job done", extra={"job_id": job_id, "status": "done"})
        except Exception as e:
            log.exception("job failed", extra={"job_id": job_id, "status": "failed"})
            store.transition(job_id, "failed", error=f"{type(e).__name__}: {e}"[:500])


if __name__ == "__main__":
    main()
