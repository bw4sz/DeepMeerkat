"""Locate source video and outputs from a run folder."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def read_parameters_csv(path: Path) -> dict[str, str]:
    """Read key/value rows from parameters.csv."""
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                out[row[0].strip()] = str(row[1]).strip()
    return out


def resolve_source_video(output_dir: Path) -> Path | None:
    """
    Find original video path for a run directory.
    Tries megadetector_results.json, fish_results.json, then parameters.csv ``source_video``.
    """
    for name in ("megadetector_results.json", "fish_results.json"):
        js = output_dir / name
        if js.is_file():
            try:
                data: dict[str, Any] = json.loads(js.read_text(encoding="utf-8"))
                v = data.get("video")
                if v:
                    p = Path(str(v))
                    if p.is_file():
                        return p
            except (OSError, json.JSONDecodeError):
                pass
    params = read_parameters_csv(output_dir / "parameters.csv")
    v = params.get("source_video")
    if v:
        p = Path(v)
        if p.is_file():
            return p
    return None


def paths_from_result_run_folder(run_folder: Path) -> tuple[Path | None, Path | None]:
    """
    Given a folder that contains ``annotations.csv`` from a prior run, return
    ``(source_video, output_parent)`` for repopulating the job form.
    ``output_parent`` is the parent of ``run_folder`` (the output directory used in the GUI).
    """
    run_folder = run_folder.resolve()
    if not (run_folder / "annotations.csv").is_file():
        return None, None
    params = read_parameters_csv(run_folder / "parameters.csv")
    sv = params.get("source_video")
    video: Path | None = Path(sv) if sv else None
    if video is not None and not video.is_file():
        video = None
    return video, run_folder.parent


def load_annotation_rows(annotations_csv: Path) -> list[dict[str, str]]:
    if not annotations_csv.is_file():
        return []
    with annotations_csv.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))
