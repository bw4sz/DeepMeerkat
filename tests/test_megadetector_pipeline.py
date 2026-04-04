from pathlib import Path
from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from deepmeerkat.config import DetectionMode, JobConfig, MegaDetectorSettings, MotionSettings


@pytest.fixture()
def tiny_video(tmp_path: Path) -> Path:
    p = tmp_path / "v.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    w = cv2.VideoWriter(str(p), fourcc, 5.0, (64, 64))
    for _ in range(8):
        w.write(np.zeros((64, 64, 3), dtype=np.uint8))
    w.release()
    return p


def test_run_megadetector_job_mocked(
    tiny_video: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake = MagicMock()

    def fake_load(*_a, **_k):
        return fake

    fake.generate_detections_one_image.return_value = {
        "file": "x",
        "detections": [
            {"bbox": [5, 5, 20, 20], "conf": 0.9, "category": "1"},
        ],
    }

    monkeypatch.setattr(
        "megadetector.detection.run_detector.load_detector",
        fake_load,
    )

    from deepmeerkat.megadetector_pipeline import run_megadetector_job

    cfg = JobConfig(
        input_path=tiny_video,
        output_dir=tmp_path / "out",
        mode=DetectionMode.MEGADETECTOR,
        megadetector=MegaDetectorSettings(max_dimension=0, frame_stride=2),
        motion=MotionSettings(),
    )
    out = run_megadetector_job(cfg)
    assert (out / "annotations.csv").is_file()
    assert (out / "parameters.csv").is_file()
