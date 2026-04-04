"""Job configuration (MegaDetector-first defaults)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class DetectionMode(StrEnum):
    MEGADETECTOR = "megadetector"
    MOTION = "motion"


@dataclass
class MegaDetectorSettings:
    """MegaDetector inference options."""

    model: str = "MDV5A"
    confidence_threshold: float = 0.25
    #: Process every Nth frame (1 = all sampled frames at video rate subject to stride).
    frame_stride: int = 1
    #: If set, overrides frame_stride when > 0 by computing stride ≈ fps / target_fps.
    target_fps: float | None = None
    write_json: bool = True
    #: Max dimension for resize before inference (0 = no resize).
    max_dimension: int = 1280
    #: Save full-frame JPEGs (with boxes) for each frame that has detections.
    save_detection_frames: bool = False


@dataclass
class MotionSettings:
    """OpenCV background subtraction (legacy-style)."""

    mog_learning_rate: float = 0.1
    mog_variance: int = 20
    #: Minimum contour area as fraction of frame area.
    min_area_fraction: float = 0.01
    use_knn: bool = False
    training_mode: bool = False
    draw_boxes: bool = False
    resize_half: bool = False


@dataclass
class JobConfig:
    """Single video or folder job."""

    input_path: Path
    output_dir: Path
    mode: DetectionMode = DetectionMode.MEGADETECTOR
    megadetector: MegaDetectorSettings = field(default_factory=MegaDetectorSettings)
    motion: MotionSettings = field(default_factory=MotionSettings)
    #: Optional ROI as (x, y, width, height) in pixels; applied after optional resize.
    roi: tuple[int, int, int, int] | None = None
    ffmpeg_path: str | None = None
