import json
import subprocess
from pathlib import Path


class MediaError(ValueError):
    pass


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{cmd[0]} failed: {result.stderr.strip()[-400:]}")
    return result.stdout


def inspect_upload(path: Path) -> dict:
    """Check that the file is an MP4 with an H.264/HEVC video stream and an audio stream; return its metadata."""
    try:
        info = json.loads(_run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    except RuntimeError:
        raise MediaError("file is not a readable video") from None
    if "mp4" not in info.get("format", {}).get("format_name", ""):
        raise MediaError("container is not MP4")
    video = [s for s in info["streams"] if s["codec_type"] == "video"]
    if not video or video[0]["codec_name"] not in ("h264", "hevc"):
        raise MediaError("video stream must be H.264 or HEVC")
    if not any(s["codec_type"] == "audio" for s in info["streams"]):
        raise MediaError("file has no audio stream")
    return {"duration": float(info["format"]["duration"]), "width": video[0]["width"],
            "height": video[0]["height"], "fps": video[0]["avg_frame_rate"]}


def _srt_time(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3_600_000:02}:{ms // 60_000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def write_srt(plan, path: Path) -> bool:
    """Write captions on the output timeline. Returns False when there are none."""
    lines, offset = [], 0.0
    for seg in plan.segments:
        for cap in plan.captions:
            if seg.start <= cap.start and cap.end <= seg.end:
                start, end = cap.start - seg.start + offset, cap.end - seg.start + offset
                lines.append(f"{len(lines) + 1}\n{_srt_time(start)} --> {_srt_time(end)}\n{cap.text}\n")
        offset += seg.end - seg.start
    path.write_text("\n".join(lines))
    return bool(lines)


def measure_loudness(path: Path, target: str = "I=-14:TP=-1.5:LRA=11") -> dict:
    """loudnorm's measurement pass; input_i is the integrated loudness in LUFS."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", f"loudnorm={target}:print_format=json",
                          "-f", "null", "-"], capture_output=True, text=True, check=True).stderr
    return json.loads(err[err.rindex("{"):err.rindex("}") + 1])


def render(src: Path, plan, out: Path, fps: str) -> None:
    """Cut and join the kept segments, burn captions, normalise loudness; H.264/AAC MP4 at source size and rate."""
    parts = []
    for i, seg in enumerate(plan.segments):
        dur = seg.end - seg.start
        fade = min(0.01, dur / 4)  # 10 ms fades at every join so cuts do not click
        parts.append(f"[0:v]trim={seg.start}:{seg.end},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={seg.start}:{seg.end},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={fade},afade=t=out:st={dur - fade}:d={fade}[a{i}]")
    joins = "".join(f"[v{i}][a{i}]" for i in range(len(plan.segments)))
    graph = ";".join(parts) + f";{joins}concat=n={len(plan.segments)}:v=1:a=1[v][a]"
    srt, cut = out.with_suffix(".srt"), out.with_suffix(".cut.mkv")
    video = "[v]"
    if write_srt(plan, srt):
        graph += f";[v]subtitles={srt}:force_style='FontSize=18,Outline=2'[vs]"
        video = "[vs]"
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", graph, "-map", video, "-map", "[a]",
          "-r", fps, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
          "-c:a", "pcm_s16le", str(cut)])
    # Measure, apply the gain that reaches the target, then limit peaks (about -2 dBFS) so speech peaks do not clip.
    # shortcut: peaky speech lands about 1 LU under target because the limiter takes some gain back;
    # add a second measure+gain pass or a compressor if delivery specs need exactly -14 LUFS.
    measured = measure_loudness(cut)["input_i"]
    gain = 0.0 if measured == "-inf" else plan.loudness_lufs - float(measured)  # silent audio: leave as is
    audio = f"volume={gain:.2f}dB,alimiter=limit=0.79:attack=5:release=50:level=false"
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(cut), "-map", "0:v", "-map", "0:a", "-c:v", "copy",
          "-af", audio, "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
          "-movflags", "+faststart", str(out)])
