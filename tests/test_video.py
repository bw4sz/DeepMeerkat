from pathlib import Path

import cv2
import numpy as np

from deepmeerkat.video import effective_stride, iter_frames, probe_video


def test_effective_stride_target_fps() -> None:
    assert effective_stride(30.0, 1, 10.0) == 3


def test_probe_and_iter_frames(tmp_path: Path) -> None:
    p = tmp_path / "t.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    w = cv2.VideoWriter(str(p), fourcc, 5.0, (32, 32))
    for _ in range(6):
        w.write(np.zeros((32, 32, 3), dtype=np.uint8))
    w.release()

    meta = probe_video(p)
    assert meta.fps > 0
    frames = list(iter_frames(p, stride=2))
    assert len(frames) == 3
