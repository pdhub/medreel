from agents.editing_planner.planner import Caption, EditPlan, Segment
from services.ffmpeg.media import inspect_upload, measure_loudness, render


def test_render_cuts_captions_and_loudness(make_video, tmp_path):
    src = make_video(seconds=3)
    plan = EditPlan(planner="test", segments=[Segment(start=0, end=1), Segment(start=2, end=3)], removed=[],
                    captions=[Caption(start=2.1, end=2.9, text="Polyuria")], flagged_terms=[])
    out = tmp_path / "out.mp4"
    render(src, plan, out, "30/1")
    meta = inspect_upload(out)
    assert abs(meta["duration"] - 2.0) < 0.1 and (meta["width"], meta["height"]) == (320, 180)
    assert abs(float(measure_loudness(out)["input_i"]) + 14) < 1.0
