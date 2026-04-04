# DeepMeerkat 3.0

Desktop and CLI tooling for ecological camera video: **MegaDetector** (default) for animal / person / vehicle bounding boxes, plus **classic OpenCV motion** mode for legacy workflows.

**Documentation:** [deepmeerkat.readthedocs.io](https://deepmeerkat.readthedocs.io/) (enable the repo on [Read the Docs](https://readthedocs.org/) using `.readthedocs.yaml`).

Development uses the **`main`** branch (and CI runs on pushes/PRs to `main`).

## DeepMeerkat 2.0 (legacy)

The previous **2.x** line is preserved as Git tag **`v2.0.0`** and branch **`v2.0`** (last state before 3.0). Use those if you need the older codebase.

## Requirements

- Python 3.11+
- For GPU inference, install PyTorch per [PyTorch](https://pytorch.org/) for your platform; `megadetector` will use it when available.

## Install

```bash
pip install -e ".[ui,dev]"
```

Run the GUI:

```bash
python -m deepmeerkat.ui
```

Run the CLI (MegaDetector is the default mode):

```bash
deepmeerkat run /path/to/video.mp4 --output ./out
```

Classic motion mode:

```bash
deepmeerkat run /path/to/video.mp4 --output ./out --mode motion
```

## Optional local smoke test

Set `DEEPMEERKAT_TEST_VIDEO` to a clip on your machine for manual checks (not used in CI).

## License

See `LICENSE`. Third-party models (MegaDetector) have their own terms; see the MegaDetector project documentation.
