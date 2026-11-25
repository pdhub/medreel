"""Editing plans: which spoken words to keep. Planners only cut; captions always come from the transcript."""
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict

FILLERS = {"um", "uh", "erm", "er", "ah", "hmm", "mm"}
SILENCE_S = 0.7
CAPTION_WORDS = 6
LOW_CONFIDENCE = 0.6


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Segment(Strict):
    start: float
    end: float


class RemovedSpan(Strict):
    start: float
    end: float
    reason: Literal["silence", "filler", "other"]


class Caption(Strict):
    start: float
    end: float
    text: str


class FlaggedTerm(Strict):
    word_index: int
    term: str
    note: str


class EditPlan(Strict):
    planner: str
    segments: list[Segment]
    removed: list[RemovedSpan]
    captions: list[Caption]
    flagged_terms: list[FlaggedTerm]
    loudness_lufs: float = -14.0


class PlanError(ValueError):
    pass


class EditPlanner(Protocol):
    def plan(self, transcript: dict) -> EditPlan: ...


def _norm(text: str) -> str:
    return text.strip(" .,!?;:\"'").lower()


def build_plan(transcript, keep, removed, flagged, planner) -> EditPlan:
    """Turn kept word ranges (inclusive index pairs) into segments, split at silences, with transcript captions."""
    words = transcript["words"]
    if not words:  # nothing spoken: nothing to cut
        return EditPlan(planner=planner, segments=[Segment(start=0, end=transcript["duration"])], removed=[],
                        captions=[], flagged_terms=[])
    removed, runs = list(removed), []
    for first, last in keep:
        run = [first]
        for i in range(first + 1, last + 1):
            if words[i]["start"] - words[i - 1]["end"] > SILENCE_S:
                removed.append(RemovedSpan(start=words[i - 1]["end"], end=words[i]["start"], reason="silence"))
                runs.append(run)
                run = []
            run.append(i)
        runs.append(run)
    segments, captions = [], []
    for run in runs:
        segments.append(Segment(start=words[run[0]]["start"], end=words[run[-1]]["end"]))
        for j in range(0, len(run), CAPTION_WORDS):
            chunk = run[j:j + CAPTION_WORDS]
            captions.append(Caption(start=words[chunk[0]]["start"], end=words[chunk[-1]]["end"],
                                    text=" ".join(words[k]["text"] for k in chunk)))
    return EditPlan(planner=planner, segments=segments, removed=sorted(removed, key=lambda r: r.start),
                    captions=captions, flagged_terms=flagged)


class RulePlanner:
    """Deterministic fallback: drop fillers and silences longer than SILENCE_S."""

    def plan(self, transcript):
        words, keep, removed, start = transcript["words"], [], [], None
        for i, w in enumerate(words):
            if _norm(w["text"]) in FILLERS:
                removed.append(RemovedSpan(start=w["start"], end=w["end"], reason="filler"))
                if start is not None:
                    keep.append((start, i - 1))
                start = None
            elif start is None:
                start = i
        if start is not None:
            keep.append((start, len(words) - 1))
        flagged = [FlaggedTerm(word_index=i, term=w["text"], note="low transcription confidence")
                   for i, w in enumerate(words) if w.get("probability", 1) < LOW_CONFIDENCE]
        return build_plan(transcript, keep, removed, flagged, "rule")


class WordRange(Strict):
    first_word: int
    last_word: int


class RemovedRange(WordRange):
    reason: Literal["filler", "other"]


class ClaudeCuts(Strict):
    keep: list[WordRange]
    removed: list[RemovedRange]
    flagged_terms: list[FlaggedTerm]


PROMPT = """You prepare edits for short educational videos recorded by medical practitioners.
Below is the transcript as numbered words. Decide which word ranges to keep, in their original order.

Rules:
- You may only cut. Never reorder, rewrite or add words.
- Cut filler words, false starts, stumbles and repeated takes (keep the best take).
- Never cut words that carry medical meaning: conditions, symptoms, tests, numbers, doses, negations, warnings.
- List every range you cut in "removed" with a reason.
- In "flagged_terms", list medical terms that look misheard or misspelled, with the word index and a short note.
  Do not correct them.

Words:
{words}"""


class ClaudePlanner:
    def __init__(self, model: str):
        import anthropic
        self.client, self.model = anthropic.Anthropic(), model

    def plan(self, transcript):
        words = transcript["words"]
        if not words:
            return build_plan(transcript, [], [], [], f"claude:{self.model}")
        listing = "\n".join(f"{i}: {w['text']}" for i, w in enumerate(words))
        response = self.client.messages.parse(
            model=self.model, max_tokens=16000, output_format=ClaudeCuts,
            messages=[{"role": "user", "content": PROMPT.format(words=listing)}])
        if response.stop_reason != "end_turn" or response.parsed_output is None:
            raise PlanError(f"planner returned no plan (stop_reason={response.stop_reason})")
        cuts = response.parsed_output
        for r in cuts.keep + cuts.removed:
            if not 0 <= r.first_word <= r.last_word < len(words):
                raise PlanError("planner returned a word index outside the transcript")
        removed = [RemovedSpan(start=words[r.first_word]["start"], end=words[r.last_word]["end"], reason=r.reason)
                   for r in cuts.removed]
        keep = sorted((r.first_word, r.last_word) for r in cuts.keep)
        return build_plan(transcript, keep, removed, cuts.flagged_terms, f"claude:{self.model}")


def get_planner(api_key: str | None, model: str) -> EditPlanner:
    return ClaudePlanner(model) if api_key else RulePlanner()


def validate_plan(plan: EditPlan, transcript: dict) -> None:
    words, duration, eps = transcript["words"], transcript["duration"], 1e-6
    if not plan.segments:
        raise PlanError("plan keeps no segments")
    starts, ends = {w["start"] for w in words}, {w["end"] for w in words}
    prev_end = 0.0
    for s in plan.segments:
        if not 0 <= s.start < s.end <= duration + eps:
            raise PlanError(f"segment {s.start}-{s.end}s is outside the source duration ({duration}s)")
        if s.start < prev_end - eps:
            raise PlanError(f"segment at {s.start}s overlaps the previous one or is out of order")
        if words and (s.start not in starts or s.end not in ends):
            raise PlanError(f"segment {s.start}-{s.end}s does not start and end on word boundaries")
        prev_end = s.end
    for c in plan.captions:
        spoken = " ".join(w["text"] for w in words if w["start"] >= c.start - eps and w["end"] <= c.end + eps)
        if c.text != spoken:
            raise PlanError(f"caption at {c.start}s is not the transcript text")  # no caption text in errors/logs
        if not any(s.start - eps <= c.start and c.end <= s.end + eps for s in plan.segments):
            raise PlanError(f"caption at {c.start}s is outside the kept segments")
    if any(not 0 <= t.word_index < len(words) for t in plan.flagged_terms):
        raise PlanError("flagged term points outside the transcript")
