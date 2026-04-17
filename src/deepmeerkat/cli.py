"""Typer CLI (MegaDetector is the default mode)."""

from __future__ import annotations

from pathlib import Path

import typer

from deepmeerkat.config import (
    DetectionMode,
    FishDetectorSettings,
    JobConfig,
    MegaDetectorSettings,
    MotionSettings,
)
from deepmeerkat.runner import run_job

app = typer.Typer(add_completion=False, help="DeepMeerkat 3.0 — ecological video processing")


@app.command("run")
def run_cmd(
    input_path: Path = typer.Argument(  # noqa: B008
        ...,
        exists=True,
        help="Video file or directory",
    ),
    output: Path = typer.Option(  # noqa: B008
        ...,
        "--output",
        "-o",
        help="Output directory",
    ),
    mode: str = typer.Option(
        "megadetector",
        "--mode",
        "-m",
        help="Detection mode: megadetector (default), fish, or motion",
    ),
    roi: str | None = typer.Option(
        None,
        "--roi",
        help="Optional region of interest: x,y,width,height",
    ),
    video_fps: float | None = typer.Option(  # noqa: B008
        None,
        "--video-fps",
        help="Override OpenCV-reported FPS (timecodes, stride, review). Omit for auto.",
    ),
    # MegaDetector
    md_model: str = typer.Option("MDV5A", "--md-model", help="MegaDetector model name or path"),
    md_conf: float = typer.Option(0.25, "--md-confidence", help="Minimum detection confidence"),
    md_stride: int = typer.Option(1, "--md-stride", help="Process every Nth frame (after FPS cap)"),
    md_target_fps: float | None = typer.Option(
        None,
        "--md-target-fps",
        help="If set, stride is chosen so processing rate ≈ this FPS",
    ),
    md_max_dim: int = typer.Option(
        1280,
        "--md-max-dimension",
        help="Resize longest side to this many pixels before inference (0 = full resolution)",
    ),
    md_json: bool = typer.Option(
        True,
        "--md-json/--no-md-json",
        help="Write megadetector_results.json",
    ),
    md_save_frames: bool = typer.Option(
        False,
        "--md-save-frames/--no-md-save-frames",
        help="Save JPEG of each frame that has detections (detection_frames/)",
    ),
    # Fish (Community Fish Detector / RF-DETR)
    fish_weights: Path | None = typer.Option(  # noqa: B008
        None,
        "--fish-weights",
        help="[fish] Weights .pth (omit to download once to the user cache)",
    ),
    fish_conf: float = typer.Option(0.3, "--fish-confidence", help="[fish] Minimum confidence"),
    fish_resolution: int = typer.Option(
        640,
        "--fish-resolution",
        help="[fish] RF-DETR input size (use 640 for released weights)",
    ),
    fish_stride: int = typer.Option(1, "--fish-stride", help="[fish] Process every Nth frame"),
    fish_target_fps: float | None = typer.Option(
        None,
        "--fish-target-fps",
        help="[fish] If set, stride ≈ video_fps / this value",
    ),
    fish_max_dim: int = typer.Option(
        1280,
        "--fish-max-dimension",
        help="[fish] Resize longest side before inference (0 = full)",
    ),
    fish_json: bool = typer.Option(
        True,
        "--fish-json/--no-fish-json",
        help="[fish] Write fish_results.json",
    ),
    fish_save_frames: bool = typer.Option(
        False,
        "--fish-save-frames/--no-fish-save-frames",
        help="[fish] Save JPEG for frames with detections",
    ),
    # Motion
    mog_lr: float = typer.Option(0.1, "--mog-learning", help="[motion] MOG learning rate"),
    mog_var: int = typer.Option(20, "--mog-variance", help="[motion] MOG variance"),
    min_area: float = typer.Option(
        0.01,
        "--min-area",
        help="[motion] Min box area as fraction of frame",
    ),
    motion_knn: bool = typer.Option(
        False,
        "--motion-knn",
        help="[motion] Use KNN background subtractor",
    ),
    training: bool = typer.Option(
        False,
        "--training",
        help="[motion] Export all motion crops only",
    ),
) -> None:
    """Process video(s) with MegaDetector (default), fish detector, or classic motion."""
    mode_e = DetectionMode(mode.lower())
    if mode_e not in (
        DetectionMode.MEGADETECTOR,
        DetectionMode.MOTION,
        DetectionMode.FISH,
    ):
        raise typer.BadParameter("mode must be megadetector, fish, or motion")

    roi_tuple: tuple[int, int, int, int] | None = None
    if roi:
        parts = [int(x.strip()) for x in roi.split(",")]
        if len(parts) != 4:
            raise typer.BadParameter("roi must be four integers: x,y,width,height")
        roi_tuple = (parts[0], parts[1], parts[2], parts[3])

    md = MegaDetectorSettings(
        model=md_model,
        confidence_threshold=md_conf,
        frame_stride=md_stride,
        target_fps=md_target_fps,
        write_json=md_json,
        max_dimension=md_max_dim,
        save_detection_frames=md_save_frames,
    )
    mo = MotionSettings(
        mog_learning_rate=mog_lr,
        mog_variance=mog_var,
        min_area_fraction=min_area,
        use_knn=motion_knn,
        training_mode=training,
    )

    fw = str(fish_weights.resolve()) if fish_weights is not None else ""
    fi = FishDetectorSettings(
        weights_path=fw,
        confidence_threshold=fish_conf,
        resolution=fish_resolution,
        frame_stride=fish_stride,
        target_fps=fish_target_fps,
        write_json=fish_json,
        max_dimension=fish_max_dim,
        save_detection_frames=fish_save_frames,
    )

    cfg = JobConfig(
        input_path=input_path,
        output_dir=output,
        mode=mode_e,
        megadetector=md,
        motion=mo,
        fish=fi,
        roi=roi_tuple,
        video_fps_override=video_fps,
    )

    def progress(p: float, msg: str) -> None:
        if int(p * 100) % 5 == 0 or p >= 1.0:
            typer.echo(f"[{p*100:5.1f}%] {msg}")

    run_job(cfg, progress=progress)
    typer.echo(typer.style("Finished.", fg=typer.colors.GREEN))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
