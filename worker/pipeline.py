from __future__ import annotations

import math
import random
import subprocess
from pathlib import Path
from typing import Any

from common.config import SEGMENT_MAX_TIMEOUT_SECONDS

MAX_DURATION_SECONDS = 600
MIN_DURATION_SECONDS = 1
SEGMENT_MIN_SECONDS = 20
SEGMENT_MAX_SECONDS = 60


class SegmentGenerationTimeoutError(TimeoutError):
    pass


def _run_command(command: list[str], timeout_seconds: int | None = None) -> None:
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise SegmentGenerationTimeoutError(f"Command timed out after {timeout_seconds}s: {' '.join(command)}") from exc


def _probe_duration(video_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return float(result.stdout.strip())


def _validate_duration(duration_sec: int) -> int:
    if not MIN_DURATION_SECONDS <= duration_sec <= MAX_DURATION_SECONDS:
        raise ValueError(f"duration_sec must be between {MIN_DURATION_SECONDS} and {MAX_DURATION_SECONDS}")
    return duration_sec


def _calculate_segment_durations(duration_sec: int) -> list[int]:
    if duration_sec <= SEGMENT_MAX_SECONDS:
        return [duration_sec]

    min_segments = math.ceil(duration_sec / SEGMENT_MAX_SECONDS)
    max_segments = duration_sec // SEGMENT_MIN_SECONDS
    for segment_count in range(min_segments, max_segments + 1):
        base = duration_sec // segment_count
        remainder = duration_sec % segment_count
        if base < SEGMENT_MIN_SECONDS:
            continue
        if base + (1 if remainder else 0) > SEGMENT_MAX_SECONDS:
            continue
        return [base + 1] * remainder + [base] * (segment_count - remainder)

    raise ValueError(f"Unable to split duration {duration_sec} into valid segments")


def _analyze_image(job: dict[str, Any]) -> dict[str, str]:
    return {
        "subject": str(job.get("subject", "main subject")),
        "background": str(job.get("background", "original scene")),
        "composition": str(job.get("composition", "center framing")),
    }


def _build_scene_plan(job: dict[str, Any], analysis: dict[str, str]) -> list[dict[str, Any]]:
    duration_sec = _validate_duration(int(job["duration_sec"]))
    segment_durations = _calculate_segment_durations(duration_sec)

    seed = int(job.get("seed", random.randint(1, 2_147_483_647)))
    camera_motion = str(job.get("camera_motion", "slow_push_in"))
    subject_lock = bool(job.get("subject_lock", True))

    scenes: list[dict[str, Any]] = []
    for index, segment_duration in enumerate(segment_durations):
        scenes.append(
            {
                "segment_index": index,
                "duration_sec": segment_duration,
                "analysis": analysis,
                "seed": seed,
                "camera_motion": camera_motion,
                "subject_lock": subject_lock,
            }
        )
    return scenes


def _render_segment(image_path: Path, segment_plan: dict[str, Any], segment_path: Path) -> None:
    _run_command(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-t",
            str(segment_plan["duration_sec"]),
            "-vf",
            "scale=1280:720,format=yuv420p",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(segment_path),
        ],
        timeout_seconds=SEGMENT_MAX_TIMEOUT_SECONDS,
    )


def _concat_segments(segment_paths: list[Path], concat_list_path: Path, output_path: Path) -> None:
    concat_list_path.write_text("".join(f"file '{path.as_posix()}'\n" for path in segment_paths), encoding="utf-8")
    _run_command(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list_path),
            "-c",
            "copy",
            str(output_path),
        ]
    )


def _trim_if_exceeds_limit(video_path: Path, max_duration_sec: float) -> None:
    actual_duration = _probe_duration(video_path)
    if actual_duration <= max_duration_sec:
        return

    trimmed_path = video_path.with_name(f"{video_path.stem}_trimmed{video_path.suffix}")
    _run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-t",
            f"{max_duration_sec:.3f}",
            "-c",
            "copy",
            str(trimmed_path),
        ]
    )
    trimmed_path.replace(video_path)


def generate_video_from_image(job: dict[str, Any]) -> dict[str, Any]:
    image_path = Path(job["image_path"])
    output_path = Path(job["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    analysis = _analyze_image(job)
    scene_plan = _build_scene_plan(job, analysis)

    segment_paths: list[Path] = []
    for segment in scene_plan:
        segment_path = output_path.parent / f"{output_path.stem}_seg_{segment['segment_index']:03d}.mp4"
        _render_segment(image_path, segment, segment_path)
        segment_paths.append(segment_path)

    concat_list_path = output_path.parent / f"{output_path.stem}_segments.txt"
    _concat_segments(segment_paths, concat_list_path, output_path)

    _trim_if_exceeds_limit(output_path, max_duration_sec=float(MAX_DURATION_SECONDS))

    return {
        "output_path": str(output_path),
        "analysis": analysis,
        "segments": scene_plan,
        "final_duration_sec": _probe_duration(output_path),
    }
