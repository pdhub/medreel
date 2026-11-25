import os
import subprocess
import tempfile

import pytest

# Must run before any app module reads settings.
os.environ["MEDREEL_DATA_DIR"] = tempfile.mkdtemp(prefix="medreel-test-")


@pytest.fixture
def make_video(tmp_path):
    def make(name="clip.mp4", seconds=2, audio=True):
        path = tmp_path / name
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=size=320x180:rate=30:duration={seconds}"]
        if audio:
            cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}", "-c:a", "aac"]
        subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", str(path)], check=True)
        return path
    return make
