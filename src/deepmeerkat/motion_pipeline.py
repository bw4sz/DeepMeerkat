"""OpenCV MOG2/KNN motion detection (secondary / legacy path)."""

from __future__ import annotations

import csv
import time
from collections.abc import Callable
from pathlib import Path
from threading import Event

import cv2
import numpy as np

from deepmeerkat.config import JobConfig
from deepmeerkat.export import write_parameters_csv
from deepmeerkat.motion_geometry import BoundingBox, contour_boxes, resize_box_crop
from deepmeerkat.timecode import frame_to_clock_str
from deepmeerkat.video import count_frames_sequential


def run_motion_job(
    config: JobConfig,
    *,
    progress: Callable[[float, str], None] | None = None,
    cancel: Event | None = None,
) -> Path:
    """Process one video with background subtraction; write frames/crops + CSVs."""
    video_path = config.input_path
    if not video_path.is_file():
        raise FileNotFoundError(f"Expected a video file for motion mode: {video_path}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = round(float(cap.get(cv2.CAP_PROP_FPS) or 30.0))
    if config.video_fps_override is not None and config.video_fps_override > 0:
        fps = round(float(config.video_fps_override))
    frame_count_est = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if frame_count_est <= 0:
        cap.release()
        frame_count_est = max(1, count_frames_sequential(video_path))
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

    stem = video_path.stem
    out_dir = config.output_dir / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    ms = config.motion
    if ms.use_knn:
        fgbg = cv2.createBackgroundSubtractorKNN()
    else:
        fgbg = cv2.createBackgroundSubtractorMOG2(
            detectShadows=False,
            varThreshold=float(ms.mog_variance),
        )
        fgbg.setBackgroundRatio(0.95)

    mog_learning = ms.mog_learning_rate
    mog_variance = ms.mog_variance
    roi_x, roi_y = (0, 0)
    if config.roi:
        roi_x, roi_y, _, _ = config.roi

    annotations: dict[int, list[BoundingBox]] = {}
    frame_idx = 0
    start = time.time()

    def report(p: float, msg: str) -> None:
        if progress:
            progress(p, msg)

    read_image: np.ndarray | None = None
    original_image: np.ndarray | None = None

    while True:
        if cancel and cancel.is_set():
            break
        ret, original_image = cap.read()
        if not ret:
            break
        frame_idx += 1
        # Legacy DeepMeerkat skipped the first frame for background init (frame_idx < 2)
        if frame_idx < 2:
            continue

        if ms.resize_half:
            read_image = cv2.resize(original_image, (0, 0), fx=0.75, fy=0.75)
        else:
            read_image = original_image.copy()

        if config.roi:
            x, y, w, h = config.roi
            read_image = read_image[y : y + h, x : x + w]

        if frame_idx % 1000 == 0 and annotations:
            recent = sum(1 for f in annotations if f > frame_idx - 1000)
            if recent / 1000.0 > 0.05:
                mog_variance = min(60, mog_variance + 5)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        if ms.use_knn:
            mask = fgbg.apply(read_image)
        else:
            mask = fgbg.apply(read_image, learningRate=mog_learning)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [c for c in contours if cv2.contourArea(c) > 50]

        if not contours:
            report(min(0.99, frame_idx / max(1, frame_count_est)), f"Frame {frame_idx}")
            continue

        boxes = contour_boxes(contours, cv2.boundingRect)
        h0, w0 = read_image.shape[:2]
        area = float(h0 * w0)
        remaining = [b for b in boxes if (b.w * b.h) >= area * ms.min_area_fraction]

        if not remaining:
            report(min(0.99, frame_idx / max(1, frame_count_est)), f"Frame {frame_idx}")
            continue

        if ms.training_mode:
            for clip_i, box in enumerate(remaining):
                clip_img = resize_box_crop(read_image, box)
                fname = out_dir / f"{stem}_{frame_idx}_{clip_i}.jpg"
                cv2.imwrite(str(fname), clip_img)
            pct = min(0.99, frame_idx / max(1, frame_count_est))
            report(pct, f"Frame {frame_idx} (training crops)")
            continue

        for box in remaining:
            box.label = ("motion", 1.0)

        # Store boxes in full-frame coordinates for CSV
        full_boxes: list[BoundingBox] = []
        for box in remaining:
            full_boxes.append(
                BoundingBox(
                    box.x + roi_x,
                    box.y + roi_y,
                    box.w,
                    box.h,
                    list(box.members),
                    box.label,
                )
            )
        annotations[frame_idx] = full_boxes

        out_frame = original_image.copy()
        if ms.draw_boxes:
            for box in remaining:
                cv2.rectangle(
                    out_frame,
                    (box.x + roi_x, box.y + roi_y),
                    (box.x + roi_x + box.w, box.y + roi_y + box.h),
                    (0, 0, 255),
                    2,
                )
        fname = out_dir / f"{frame_idx}.jpg"
        cv2.imwrite(str(fname), out_frame)

        report(min(0.99, frame_idx / max(1, frame_count_est)), f"Motion frame {frame_idx}")

    cap.release()
    end = time.time()

    rows = []
    for fr in sorted(annotations):
        clock = frame_to_clock_str(fr, float(fps))
        for bbox in annotations[fr]:
            lab = bbox.label[0] or ""
            sc = bbox.label[1] if bbox.label[1] is not None else ""
            rows.append(
                {
                    "frame": fr,
                    "clock": clock,
                    "x": bbox.x,
                    "y": bbox.y,
                    "h": bbox.h,
                    "w": bbox.w,
                    "label": lab,
                    "score": sc,
                }
            )

    ann_path = out_dir / "annotations.csv"
    with ann_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["frame", "clock", "x", "y", "h", "w", "label", "score"],
        )
        w.writeheader()
        w.writerows(rows)

    params = {
        "mode": "motion",
        "source_video": str(video_path.resolve()),
        "mog_learning_rate": mog_learning,
        "mog_variance": mog_variance,
        "min_area_fraction": ms.min_area_fraction,
        "use_knn": ms.use_knn,
        "training_mode": ms.training_mode,
        "minutes": (end - start) / 60.0,
        "total_frames": frame_idx,
        "motion_events": len(annotations),
        "video_fps": fps,
        "video_fps_override": config.video_fps_override or "",
    }
    write_parameters_csv(out_dir / "parameters.csv", params)
    report(1.0, "Done.")
    return out_dir
