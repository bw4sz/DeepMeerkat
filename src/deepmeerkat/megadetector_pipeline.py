"""MegaDetector-based video processing (primary path)."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from threading import Event
from typing import Any

import cv2

from deepmeerkat.config import JobConfig
from deepmeerkat.export import write_annotations_csv, write_json, write_parameters_csv
from deepmeerkat.labels import category_label
from deepmeerkat.timecode import frame_to_clock_str
from deepmeerkat.video import bgr_to_rgb, effective_stride, iter_frames, probe_video


def _bgr_color_for_label(name: str) -> tuple[int, int, int]:
    n = name.lower()
    if n == "person":
        return (220, 120, 52)
    if n == "vehicle":
        return (34, 126, 230)
    return (99, 180, 40)


def run_megadetector_job(
    config: JobConfig,
    *,
    progress: Callable[[float, str], None] | None = None,
    cancel: Event | None = None,
) -> Path:
    """
    Run MegaDetector on a video file; write JSON + annotations.csv + parameters.csv under output.
    """
    from megadetector.detection import run_detector

    video_path = config.input_path
    if not video_path.is_file():
        raise FileNotFoundError(f"Expected a video file for MegaDetector mode: {video_path}")

    meta = probe_video(video_path)
    stride = effective_stride(
        meta.fps,
        config.megadetector.frame_stride,
        config.megadetector.target_fps,
    )
    roi_x, roi_y = (0, 0)
    if config.roi:
        roi_x, roi_y, _, _ = config.roi

    stem = video_path.stem
    out_dir = config.output_dir / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    def report(p: float, msg: str) -> None:
        if progress:
            progress(p, msg)

    report(0.0, "Loading MegaDetector model…")
    detector = run_detector.load_detector(
        config.megadetector.model,
        force_cpu=False,
        force_model_download=False,
        verbose=False,
    )

    max_dim = int(config.megadetector.max_dimension)

    results: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    t0 = time.time()
    frame_total_guess = max(1, meta.frame_count // stride)

    processed = 0
    for frame_idx, frame_bgr in iter_frames(
        video_path,
        stride,
        resize_half=False,
        roi=config.roi,
        max_dimension=max_dim if max_dim > 0 else 0,
    ):
        if cancel and cancel.is_set():
            report(1.0, "Cancelled.")
            break

        rgb = bgr_to_rgb(frame_bgr)
        image_id = f"{stem}_frame_{frame_idx:06d}"
        det_thresh = max(0.00001, float(config.megadetector.confidence_threshold))

        res = detector.generate_detections_one_image(
            rgb,
            image_id=image_id,
            detection_threshold=det_thresh,
            image_size=None,
            augment=False,
            verbose=False,
        )
        results.append(res)

        clock = frame_to_clock_str(frame_idx, meta.fps)
        for det in res.get("detections") or []:
            x, y, w, h = det["bbox"]
            x, y = x + roi_x, y + roi_y
            lab = category_label(det["category"])
            csv_rows.append(
                {
                    "frame": frame_idx,
                    "clock": clock,
                    "x": int(round(x)),
                    "y": int(round(y)),
                    "h": int(round(h)),
                    "w": int(round(w)),
                    "label": lab,
                    "score": det["conf"],
                }
            )

        if config.megadetector.save_detection_frames and res.get("detections"):
            det_dir = out_dir / "detection_frames"
            det_dir.mkdir(exist_ok=True)
            vis = frame_bgr.copy()
            for det in res["detections"]:
                x, y, w, h = det["bbox"]
                xi, yi, wi, hi = int(x), int(y), int(w), int(h)
                lab = category_label(det["category"])
                col = _bgr_color_for_label(lab)
                cv2.rectangle(vis, (xi, yi), (xi + wi, yi + hi), col, 2)
                cv2.putText(
                    vis,
                    lab,
                    (xi, max(16, yi - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    col,
                    2,
                    cv2.LINE_AA,
                )
            cv2.imwrite(str(det_dir / f"frame_{frame_idx:06d}.jpg"), vis)

        processed += 1
        frac = min(0.99, processed / float(frame_total_guess))
        report(frac, f"Frame {frame_idx} ({processed} processed)")

    elapsed = time.time() - t0

    if config.megadetector.write_json:
        write_json(
            out_dir / "megadetector_results.json",
            {"images": results, "video": str(video_path)},
        )

    write_annotations_csv(
        out_dir / "annotations.csv",
        csv_rows,
        fieldnames=["frame", "clock", "x", "y", "h", "w", "label", "score"],
    )

    params = {
        "mode": "megadetector",
        "source_video": str(video_path.resolve()),
        "model": config.megadetector.model,
        "confidence_threshold": config.megadetector.confidence_threshold,
        "frame_stride_setting": config.megadetector.frame_stride,
        "target_fps": config.megadetector.target_fps,
        "effective_stride": stride,
        "video_fps": meta.fps,
        "minutes": elapsed / 60.0,
        "frames_processed": processed,
        "detections": len(csv_rows),
        "save_detection_frames": config.megadetector.save_detection_frames,
    }
    write_parameters_csv(out_dir / "parameters.csv", params)

    report(1.0, "Done.")
    return out_dir
