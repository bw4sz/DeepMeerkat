"""Video frame iteration and metadata."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class VideoMeta:
    path: Path
    fps: float
    width: int
    height: int
    frame_count: int
    #: True when frame_count came from the container (OpenCV); False when counted by scan.
    frame_count_from_metadata: bool = True


def count_frames_sequential(path: Path) -> int:
    """Count frames by decoding sequentially (for containers with broken CAP_PROP_FRAME_COUNT)."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return 0
    n = 0
    while True:
        ret, _ = cap.read()
        if not ret:
            break
        n += 1
    cap.release()
    return n


def probe_video(path: Path, *, fps_override: float | None = None) -> VideoMeta:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0) or 30.0
    if fps_override is not None and fps_override > 0:
        fps = float(fps_override)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    cap.release()
    from_metadata = n > 0
    if n <= 0:
        n = count_frames_sequential(path)
        from_metadata = False
    return VideoMeta(
        path=path,
        fps=fps,
        width=width,
        height=height,
        frame_count=max(1, n),
        frame_count_from_metadata=from_metadata,
    )


def effective_stride(fps: float, frame_stride: int, target_fps: float | None) -> int:
    if target_fps is not None and target_fps > 0 and fps > 0:
        s = max(1, int(round(fps / target_fps)))
        return s
    return max(1, frame_stride)


def iter_frames(
    path: Path,
    stride: int,
    *,
    resize_half: bool = False,
    roi: tuple[int, int, int, int] | None = None,
    max_dimension: int = 0,
) -> Iterator[tuple[int, np.ndarray]]:
    """
    Yield (frame_index, image_bgr) for frames 1..N (1-based index matches legacy logging).
    """
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        idx += 1
        if stride > 1 and (idx - 1) % stride != 0:
            continue
        if resize_half:
            frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
        if roi is not None:
            x, y, w, h = roi
            frame = frame[y : y + h, x : x + w]
        if max_dimension > 0:
            h, w = frame.shape[:2]
            m = max(h, w)
            if m > max_dimension:
                scale = max_dimension / m
                frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
        yield idx, frame
    cap.release()


def bgr_to_rgb(image_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
