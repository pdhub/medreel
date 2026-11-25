"""End-to-end check against a running stack: python tests/end_to_end/e2e.py [base_url]

Generates a synthetic 10 s clip (test pattern + tone, no real person), runs the full job flow and
checks the output with ffprobe.
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
TIMEOUT_S = 900


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    c = httpx.Client(base_url=BASE, timeout=120)
    assert c.get("/health").status_code == 200, "health check failed"
    with tempfile.TemporaryDirectory() as d:
        src, out = Path(d, "in.mp4"), Path(d, "out.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=30:duration=10",
                        "-f", "lavfi", "-i", "sine=frequency=440:duration=10", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(src)], check=True)

        bad = c.post("/api/jobs").json()["job_id"]
        assert c.post(f"/api/jobs/{bad}/start").status_code == 409, "start before upload must be 409"
        r = c.post(f"/api/jobs/{bad}/upload", files={"file": ("notes.txt", b"hello", "text/plain")})
        assert r.status_code == 415, f"non-MP4 upload must be 415, got {r.status_code}"

        job = c.post("/api/jobs").json()["job_id"]
        with open(src, "rb") as f:
            r = c.post(f"/api/jobs/{job}/upload", files={"file": ("in.mp4", f, "video/mp4")})
        assert r.status_code == 200, r.text
        assert c.post(f"/api/jobs/{job}/start").status_code == 202
        started, seen = time.time(), []
        while (status := c.get(f"/api/jobs/{job}").json())["status"] not in ("done", "failed"):
            if not seen or seen[-1] != status["status"]:
                seen.append(status["status"])
            assert time.time() - started < TIMEOUT_S, f"timed out in {status['status']}"
            time.sleep(2)
        assert status["status"] == "done", f"job failed: {status['error']}"

        transcript = c.get(f"/api/jobs/{job}/transcript").json()
        plan = c.get(f"/api/jobs/{job}/editing-plan").json()
        r = c.get(f"/api/jobs/{job}/output")
        assert r.status_code == 200 and r.headers["content-type"] == "video/mp4"
        out.write_bytes(r.content)

        info, src_info = probe(out), probe(src)
        codecs = {s["codec_type"]: s["codec_name"] for s in info["streams"]}
        assert codecs == {"video": "h264", "audio": "aac"}, codecs
        out_s, in_s = float(info["format"]["duration"]), float(src_info["format"]["duration"])
        assert 0 < out_s <= in_s + 0.1, f"output {out_s}s vs input {in_s}s"
        video = next(s for s in info["streams"] if s["codec_type"] == "video")
        assert (video["width"], video["height"]) == (640, 360)
        print("E2E PASS", json.dumps({"job_id": job, "statuses_seen": seen, "seconds": round(time.time() - started, 1),
                                      "words": len(transcript["words"]), "planner": plan["planner"],
                                      "segments": len(plan["segments"]), "input_s": in_s, "output_s": out_s,
                                      "output_fps": video["avg_frame_rate"]}))


if __name__ == "__main__":
    main()
