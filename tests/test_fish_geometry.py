"""Geometry helpers for fish pipeline (no rfdetr import)."""

from pathlib import Path

from deepmeerkat.fish_pipeline import bbox_xyxy_to_video_pixels
from deepmeerkat.video import VideoMeta


def test_bbox_xyxy_full_frame() -> None:
    meta = VideoMeta(path=Path("/tmp/v.mp4"), fps=30.0, width=1920, height=1080, frame_count=100)
    # Inference frame 960x540 (half size)
    x, y, w, h = bbox_xyxy_to_video_pixels(10, 20, 110, 120, (540, 960), meta, None)
    assert x == 20
    assert y == 40
    assert w == 200
    assert h == 200


def test_bbox_xyxy_with_roi() -> None:
    meta = VideoMeta(path=Path("/tmp/v.mp4"), fps=30.0, width=1920, height=1080, frame_count=100)
    roi = (100, 50, 800, 600)
    # Detection in 400x300 inference crop
    x, y, w, h = bbox_xyxy_to_video_pixels(10, 10, 50, 70, (300, 400), meta, roi)
    assert x == 120
    assert y == 70
    assert w == 80
    assert h == 120
