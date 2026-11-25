import pytest

from agents.editing_planner.planner import (Caption, EditPlan, PlanError, RulePlanner, Segment, validate_plan)


def w(text, start, end, p=0.9):
    return {"text": text, "start": start, "end": end, "probability": p}


TRANSCRIPT = {"duration": 6.0, "words": [
    w("Diabetes", 0.2, 0.8), w("um", 0.9, 1.1), w("is", 1.2, 1.4), w("common.", 1.5, 2.0),
    w("Check", 3.5, 3.9), w("HbA1c.", 4.0, 4.6, p=0.4)]}


def test_rule_planner_cuts_fillers_and_silences():
    plan = RulePlanner().plan(TRANSCRIPT)
    assert [(s.start, s.end) for s in plan.segments] == [(0.2, 0.8), (1.2, 2.0), (3.5, 4.6)]
    assert {r.reason for r in plan.removed} == {"filler", "silence"}
    assert [c.text for c in plan.captions] == ["Diabetes", "is common.", "Check HbA1c."]
    assert [t.term for t in plan.flagged_terms] == ["HbA1c."]
    validate_plan(plan, TRANSCRIPT)


def test_no_speech_keeps_whole_video():
    plan = RulePlanner().plan({"duration": 10.0, "words": []})
    assert [(s.start, s.end) for s in plan.segments] == [(0, 10.0)]
    validate_plan(plan, {"duration": 10.0, "words": []})


def plan_with(segments, captions=()):
    return EditPlan(planner="test", segments=[Segment(start=a, end=b) for a, b in segments],
                    removed=[], captions=list(captions), flagged_terms=[])


@pytest.mark.parametrize("segments, message", [
    ([(0.2, 7.0)], "outside the source duration"),
    ([(1.2, 2.0), (0.2, 0.8)], "overlaps"),
    ([(0.3, 0.8)], "word boundaries"),
    ([], "no segments"),
])
def test_validate_rejects_bad_segments(segments, message):
    with pytest.raises(PlanError, match=message):
        validate_plan(plan_with(segments), TRANSCRIPT)


def test_validate_rejects_invented_caption_text():
    plan = plan_with([(0.2, 0.8)], [Caption(start=0.2, end=0.8, text="Diabetes is curable")])
    with pytest.raises(PlanError, match="not the transcript"):
        validate_plan(plan, TRANSCRIPT)
