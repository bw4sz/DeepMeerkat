"""CSV / JSON export helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def write_parameters_csv(path: Path, params: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for k, v in sorted(params.items()):
            w.writerow([k, v])


def write_annotations_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: list[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        fn = fieldnames or [
            "frame",
            "clock",
            "x",
            "y",
            "h",
            "w",
            "label",
            "score",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fn).writeheader()
        return
    fn = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        dw = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
        dw.writeheader()
        for r in rows:
            dw.writerow({k: r.get(k, "") for k in fn})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
