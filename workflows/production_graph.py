"""Day 1 pipeline: transcribe -> plan -> validate_plan -> render. Each node persists its artifact."""
import logging
import tempfile
import time
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from agents.editing_planner.planner import EditPlan, EditPlanner, validate_plan
from services.ffmpeg.media import render
from services.jobs.store import JobStore
from services.storage.backend import StorageBackend, get_json, put_json
from services.transcription.whisper import Transcriber

log = logging.getLogger("medreel.pipeline")


class State(TypedDict):
    job_id: str


def build_graph(store: JobStore, storage: StorageBackend, transcriber: Transcriber, planner: EditPlanner, tmp_dir):
    def node(name, status, fn):
        def run(state: State) -> State:
            job_id = state["job_id"]
            if status:
                store.transition(job_id, status)
            started = time.monotonic()
            log.info("node started", extra={"job_id": job_id, "node": name})
            fn(job_id)
            log.info("node finished", extra={"job_id": job_id, "node": name,
                                             "duration_s": round(time.monotonic() - started, 2)})
            return state
        return run

    def transcribe(job_id):
        meta = get_json(storage, f"{job_id}/source.json")
        transcript = transcriber.transcribe(storage.get(f"{job_id}/source.mp4"))
        for w in transcript["words"]:  # Whisper can overshoot the media end slightly
            w["end"] = min(w["end"], meta["duration"])
        put_json(storage, f"{job_id}/transcript.json", {**transcript, "duration": meta["duration"]})

    def plan(job_id):
        transcript = get_json(storage, f"{job_id}/transcript.json")
        put_json(storage, f"{job_id}/plan.json", planner.plan(transcript).model_dump())

    def check(job_id):
        validate_plan(EditPlan(**get_json(storage, f"{job_id}/plan.json")),
                      get_json(storage, f"{job_id}/transcript.json"))

    def render_output(job_id):
        meta = get_json(storage, f"{job_id}/source.json")
        with tempfile.TemporaryDirectory(dir=tmp_dir) as work:
            out = f"{work}/output.mp4"
            render(storage.get(f"{job_id}/source.mp4"), EditPlan(**get_json(storage, f"{job_id}/plan.json")),
                   Path(out), meta["fps"])
            with open(out, "rb") as f:
                storage.put(f"{job_id}/output.mp4", f)
        store.transition(job_id, "done")

    graph = StateGraph(State)
    # The worker claims a job straight into "transcribing", so the first node sets no status.
    graph.add_node("transcribe", node("transcribe", None, transcribe))
    graph.add_node("plan", node("plan", "planning", plan))
    graph.add_node("validate_plan", node("validate_plan", None, check))
    graph.add_node("render", node("render", "rendering", render_output))
    graph.add_edge(START, "transcribe")
    graph.add_edge("transcribe", "plan")
    graph.add_edge("plan", "validate_plan")
    graph.add_edge("validate_plan", "render")
    graph.add_edge("render", END)
    return graph.compile()
