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

**Community Fish Detector** (underwater; requires `[fish]` extras and a downloaded `.pth` — see [fish.md](fish.md)):

```bash
deepmeerkat run /path/to/video.avi --output ./out --mode fish \
  --fish-weights /path/to/community-fish-detector-*.pth
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

Full help: `deepmeerkat run --help`.

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
