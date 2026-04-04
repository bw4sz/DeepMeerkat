"""Filter annotation rows for the review UI (pure helpers, testable)."""

from __future__ import annotations


def parse_frame(row: dict[str, str]) -> int | None:
    try:
        return int(float(row.get("frame", "")))
    except (TypeError, ValueError):
        return None


def parse_score(row: dict[str, str]) -> float:
    raw = row.get("score", "")
    if raw is None or str(raw).strip() == "":
        return 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def filter_annotation_rows(
    rows: list[dict[str, str]],
    *,
    label: str | None,
    min_score: float,
) -> list[dict[str, str]]:
    """
    Keep rows matching optional label (None or \"All\" = any) and score >= min_score.
    """
    want_label = (label or "").strip()
    all_labels = want_label == "" or want_label.lower() == "all"
    out: list[dict[str, str]] = []
    for r in rows:
        if parse_frame(r) is None:
            continue
        if not all_labels:
            lab = str(r.get("label", "")).strip()
            if lab.lower() != want_label.lower():
                continue
        if parse_score(r) < min_score:
            continue
        out.append(r)
    return out


def sorted_unique_frames(rows: list[dict[str, str]]) -> list[int]:
    frames: set[int] = set()
    for r in rows:
        f = parse_frame(r)
        if f is not None:
            frames.add(f)
    return sorted(frames)


def unique_labels(rows: list[dict[str, str]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for r in rows:
        if parse_frame(r) is None:
            continue
        lab = str(r.get("label", "")).strip()
        if lab and lab not in seen:
            seen.add(lab)
            ordered.append(lab)
    return sorted(ordered, key=str.lower)
