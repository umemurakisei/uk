import argparse
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

MAX_DURATION_SECONDS = 600
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 30


def validate_duration(duration: int) -> int:
    if duration < 1 or duration > MAX_DURATION_SECONDS:
        raise ValueError(f"duration must be between 1 and {MAX_DURATION_SECONDS} seconds")
    return duration


def build_ffmpeg_command(
    image_path: Path,
    output_path: Path,
    duration: int,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int = DEFAULT_FPS,
) -> list[str]:
    # Gentle zoom/pan effect so a still image feels like a video sequence.
    zoom_expr = "zoom='min(zoom+0.0008,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    frames = duration * fps
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan={zoom_expr}:d={frames}:s={width}x{height}:fps={fps},"
        "format=yuv420p"
    )

    return [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-vf",
        "".join(vf),
        "-t",
        str(duration),
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]


def generate_video(image_path: Path, output_path: Path, duration: int) -> None:
    validate_duration(duration)
    if not image_path.exists():
        raise FileNotFoundError(f"image file not found: {image_path}")

    command = build_ffmpeg_command(image_path, output_path, duration)
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed. stderr:\n"
            f"{completed.stderr.strip() or '(no stderr output)'}"
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an MP4 video from one image. "
            f"Duration is limited to {MAX_DURATION_SECONDS} seconds (10 minutes)."
        )
    )
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--output", required=True, help="Path to output mp4 file")
    parser.add_argument(
        "--duration",
        required=True,
        type=int,
        help="Video duration in seconds (1-600)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        generate_video(Path(args.image), Path(args.output), int(args.duration))
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
