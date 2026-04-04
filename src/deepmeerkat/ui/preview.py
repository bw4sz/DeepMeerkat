"""First-frame preview from video files."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap


def pixmap_from_video_first_frame(
    video_path: Path,
    *,
    max_width: int = 520,
    max_height: int = 292,
) -> QPixmap | None:
    """Read the first decodable frame and return a scaled pixmap, or None."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return None
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = np.ascontiguousarray(rgb)
    h, w, ch = rgb.shape
    qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
    pix = QPixmap.fromImage(qimg.copy())
    return pix.scaled(
        max_width,
        max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def first_video_in_folder(folder: Path) -> Path | None:
    """Return first video file path in folder (shallow + rglob), or None."""
    suffixes = {".mp4", ".avi", ".mov", ".mkv", ".m4v", ".tlv"}
    if not folder.is_dir():
        return None
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in suffixes:
            return p
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.suffix.lower() in suffixes:
            return p
    return None
