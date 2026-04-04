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
    Tries megadetector_results.json, then parameters.csv ``source_video``.
    """
    js = output_dir / "megadetector_results.json"
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


def load_annotation_rows(annotations_csv: Path) -> list[dict[str, str]]:
    if not annotations_csv.is_file():
        return []
    with annotations_csv.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))
