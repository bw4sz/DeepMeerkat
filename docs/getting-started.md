# Getting started

## Requirements

- **Python 3.11+**
- For GPU acceleration, install **PyTorch** for your platform ([pytorch.org](https://pytorch.org/)). On Apple Silicon, PyTorch uses **MPS** (Metal); on NVIDIA Linux/Windows, **CUDA** when available.

## Install

From **[PyPI](https://pypi.org/project/deepmeerkat/)** (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install "deepmeerkat[ui]"
```

**Development** (editable install from a clone):

```bash
git clone https://github.com/bw4sz/DeepMeerkat.git
cd DeepMeerkat
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[ui]"
```

## CLI (MegaDetector default)

```bash
deepmeerkat run /path/to/video.mp4 --output ./out
```

**Community Fish Detector** (underwater; requires `[fish]` extras — weights download automatically on first run; see [fish.md](fish.md)):

```bash
deepmeerkat run /path/to/video.avi --output ./out --mode fish
```

Classic motion mode:

```bash
deepmeerkat run /path/to/video.mp4 --output ./out --mode motion
```

Useful options:

| Option | Purpose |
|--------|---------|
| `--md-stride N` | Process every Nth frame |
| `--md-target-fps X` | Auto-stride to approximate X FPS |
| `--md-save-frames` | Save JPEGs for frames that have detections (`detection_frames/`) |
| `--video-fps X` | Override OpenCV-reported FPS (timecodes, stride with target FPS, review playback) |

Full help: `deepmeerkat run --help`.

### Unusual video (e.g. `.tlv`) and wrong FPS in the file

Some containers report **no frame count** (`CAP_PROP_FRAME_COUNT` is 0) or **broken random seek** in OpenCV. DeepMeerkat **scans the file once** to count frames when needed (so the progress bar and stride math stay sane), and the **Review** window **decodes sequentially** for those runs so the image matches the frame index. Scrubbing to a frame far ahead can take a few seconds on long clips.

If **timestamps or stride** still look wrong because the declared FPS does not match reality (for example true 1 fps but metadata says 10), use **Video timing → FPS override** in the desktop app or `--video-fps` on the CLI. The value is stored in `parameters.csv` as `video_fps_override` for the next review session.

## Desktop app

```bash
deepmeerkat-gui
# or
python -m deepmeerkat.ui
```

Pick input video (or folder), output folder, and run. After a run, choose **Open folder** or **Review detections** to scrub the video and jump to rows in `annotations.csv`. Use **File → Review results folder…** to open an existing output directory.

See **[Review detections](review.md)** for filters, keyboard shortcuts (frame stepping and playback), and the detection navigation buttons.

## Outputs

Each video gets a subfolder under your output directory with `annotations.csv`, `parameters.csv`, and (MegaDetector) `megadetector_results.json` unless disabled.

## Read the Docs

Enable this repository on [Read the Docs](https://readthedocs.org/) and point it at the included `.readthedocs.yaml` (MkDocs). Documentation builds from the `docs/` folder.
