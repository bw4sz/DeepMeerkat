"""Community Fish Detector (RF-DETR) — underwater / fish-only video path."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from threading import Event
from typing import Any

import cv2

from deepmeerkat.config import JobConfig
from deepmeerkat.export import write_annotations_csv, write_json, write_parameters_csv
from deepmeerkat.fish_weights import ensure_fish_weights
from deepmeerkat.timecode import frame_to_clock_str
from deepmeerkat.video import VideoMeta, bgr_to_rgb, effective_stride, iter_frames, probe_video


def _try_import_rfdetr() -> Any:
    try:
        from rfdetr import RFDETRNano
    except ImportError as e:
        raise ImportError(
            "Community Fish Detector requires optional dependencies. Install with:\n"
            '  pip install "deepmeerkat[fish]"'
        ) from e
    return RFDETRNano


def bbox_xyxy_to_video_pixels(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    frame_hw: tuple[int, int],
    meta: VideoMeta,
    roi: tuple[int, int, int, int] | None,
) -> tuple[int, int, int, int]:
    """
    Map detection box from inference frame (ROI-cropped / resized) to full-video pixels.
    """
    hf, wf = frame_hw[0], frame_hw[1]
    if roi:
        rx, ry, rw, rh = roi
        sx = rw / float(wf)
        sy = rh / float(hf)
        X1 = rx + x1 * sx
        Y1 = ry + y1 * sy
        X2 = rx + x2 * sx
        Y2 = ry + y2 * sy
    else:
        sx = meta.width / float(wf)
        sy = meta.height / float(hf)
        X1 = x1 * sx
        Y1 = y1 * sy
        X2 = x2 * sx
        Y2 = y2 * sy
    x = int(round(X1))
    y = int(round(Y1))
    w = int(round(X2 - X1))
    h = int(round(Y2 - Y1))
    return x, y, w, h


def _bgr_color_fish() -> tuple[int, int, int]:
    return (255, 180, 60)


def run_fish_job(
    config: JobConfig,
    *,
    progress: Callable[[float, str], None] | None = None,
    cancel: Event | None = None,
) -> Path:
    """Run Community Fish Detector on a video; write JSON + annotations.csv + parameters.csv."""
    RFDETRNano = _try_import_rfdetr()

    video_path = config.input_path
    if not video_path.is_file():
        raise FileNotFoundError(f"Expected a video file for fish mode: {video_path}")

    def report(p: float, msg: str) -> None:
        if progress:
            progress(p, msg)

    def ensure_prog(p: float, msg: str) -> None:
        report(min(0.99, p * 0.08), msg)

    weights = ensure_fish_weights(
        config.fish.weights_path,
        progress=ensure_prog if progress else None,
        cancel=cancel,
    )

    meta = probe_video(video_path)
    stride = effective_stride(
        meta.fps,
        config.fish.frame_stride,
        config.fish.target_fps,
    )
    fish = config.fish

    stem = video_path.stem
    out_dir = config.output_dir / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    report(0.08, "Loading Community Fish Detector (RF-DETR)…")
    res = int(fish.resolution)
    model = RFDETRNano(pretrain_weights=str(weights), resolution=res)
    from PIL import Image

    max_dim = int(fish.max_dimension)
    thresh = max(0.00001, float(fish.confidence_threshold))

    csv_rows: list[dict[str, Any]] = []
    json_images: list[dict[str, Any]] = []
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
        pil = Image.fromarray(rgb)

        detections = model.predict(pil, threshold=thresh)
        hf, wf = frame_bgr.shape[0], frame_bgr.shape[1]
        clock = frame_to_clock_str(frame_idx, meta.fps)

        dets_out: list[dict[str, Any]] = []
        n = len(detections) if detections is not None else 0
        for i in range(n):
            xyxy = detections.xyxy[i]
            x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
            conf = float(detections.confidence[i])
            x, y, w, h = bbox_xyxy_to_video_pixels(
                x1, y1, x2, y2,
                (hf, wf),
                meta,
                config.roi,
            )
            csv_rows.append(
                {
                    "frame": frame_idx,
                    "clock": clock,
                    "x": x,
                    "y": y,
                    "h": h,
                    "w": w,
                    "label": "fish",
                    "score": conf,
                }
            )
            dets_out.append(
                {
                    "bbox": [x, y, w, h],
                    "conf": conf,
                    "category": "fish",
                }
            )

        json_images.append(
            {
                "file": f"{stem}_frame_{frame_idx:06d}",
                "detections": dets_out,
            }
        )

        if fish.save_detection_frames and dets_out:
            det_dir = out_dir / "detection_frames"
            det_dir.mkdir(exist_ok=True)
            vis = frame_bgr.copy()
            for i in range(n):
                xyxy = detections.xyxy[i]
                xi1, yi1, xi2, yi2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                col = _bgr_color_fish()
                cv2.rectangle(vis, (xi1, yi1), (xi2, yi2), col, 2)
                cv2.putText(
                    vis,
                    "fish",
                    (xi1, max(16, yi1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    col,
                    2,
                    cv2.LINE_AA,
                )
            cv2.imwrite(str(det_dir / f"frame_{frame_idx:06d}.jpg"), vis)

        processed += 1
        span = 0.91
        base = 0.08
        frac = base + min(span, (processed / float(frame_total_guess)) * span)
        report(frac, f"Frame {frame_idx} ({processed} processed)")

    elapsed = time.time() - t0

    if fish.write_json:
        write_json(
            out_dir / "fish_results.json",
            {
                "video": str(video_path.resolve()),
                "detector": "community-fish-detector-rf-detr-nano",
                "images": json_images,
            },
        )

    write_annotations_csv(
        out_dir / "annotations.csv",
        csv_rows,
        fieldnames=["frame", "clock", "x", "y", "h", "w", "label", "score"],
    )

    params = {
        "mode": "fish",
        "source_video": str(video_path.resolve()),
        "fish_weights": str(weights.resolve()),
        "fish_resolution": res,
        "confidence_threshold": fish.confidence_threshold,
        "frame_stride_setting": fish.frame_stride,
        "target_fps": fish.target_fps,
        "effective_stride": stride,
        "video_fps": meta.fps,
        "minutes": elapsed / 60.0,
        "frames_processed": processed,
        "detections": len(csv_rows),
        "max_dimension": fish.max_dimension,
        "save_detection_frames": fish.save_detection_frames,
    }
    write_parameters_csv(out_dir / "parameters.csv", params)

    report(1.0, "Done.")
    return out_dir
