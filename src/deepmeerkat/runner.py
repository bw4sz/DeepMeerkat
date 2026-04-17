"""Dispatch jobs by detection mode."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from threading import Event

from deepmeerkat.config import DetectionMode, JobConfig
from deepmeerkat.fish_pipeline import run_fish_job
from deepmeerkat.megadetector_pipeline import run_megadetector_job
from deepmeerkat.motion_pipeline import run_motion_job

VIDEO_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".m4v", ".tlv"}


def iter_video_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(path)
    out: list[Path] = []
    for p in sorted(path.rglob("*")):
        if p.is_file() and p.suffix.lower() in VIDEO_SUFFIXES:
            out.append(p)
    return out


def run_job(
    config: JobConfig,
    *,
    progress: Callable[[float, str], None] | None = None,
    cancel: Event | None = None,
) -> list[Path]:
    """Run processing for each video under input path; returns output directory paths."""
    config.output_dir.mkdir(parents=True, exist_ok=True)
    paths = iter_video_paths(config.input_path)
    if not paths:
        raise FileNotFoundError(f"No video files found under {config.input_path}")

    results: list[Path] = []
    n = len(paths)
    for i, vp in enumerate(paths):
        sub = JobConfig(
            input_path=vp,
            output_dir=config.output_dir,
            mode=config.mode,
            megadetector=config.megadetector,
            motion=config.motion,
            fish=config.fish,
            roi=config.roi,
            ffmpeg_path=config.ffmpeg_path,
            video_fps_override=config.video_fps_override,
        )

        def on_progress(p: float, msg: str, _i: int = i) -> None:
            if progress:
                progress((_i + p) / n, msg)

        if config.mode == DetectionMode.MEGADETECTOR:
            results.append(run_megadetector_job(sub, progress=on_progress, cancel=cancel))
        elif config.mode == DetectionMode.FISH:
            results.append(run_fish_job(sub, progress=on_progress, cancel=cancel))
        else:
            results.append(run_motion_job(sub, progress=on_progress, cancel=cancel))
    return results
