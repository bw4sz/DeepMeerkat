# DeepMeerkat 3.0

Desktop and CLI tooling for ecological camera video: **MegaDetector** (default) for animal / person / vehicle bounding boxes, plus **classic OpenCV motion** mode for legacy workflows.

**Documentation:** [deepmeerkat.readthedocs.io](https://deepmeerkat.readthedocs.io/) (enable the repo on [Read the Docs](https://readthedocs.org/) using `.readthedocs.yaml`).

Development uses the **`main`** branch (and CI runs on pushes/PRs to `main`).

## Version history (why “3.0”?)

This codebase is released as **DeepMeerkat 3.0** and is the modern “**Meerkat 3**” line:

| Line | What it refers to |
|------|-------------------|
| **1.0** | **MotionMeerkat** — earlier motion-focused tooling in the same research lineage. |
| **2.0** | **DeepMeerkat** — the previous desktop/codebase generation, preserved as Git tag **`v2.0.0`** and branch **`v2.0`**. |
| **3.0** | **DeepMeerkat 3.0** (this repository) — MegaDetector-first PySide6 GUI and CLI, rewritten packaging and outputs. |

We **start numbering releases at 3.0** here so installers and PyPI stay aligned with that story (not with MotionMeerkat or legacy DeepMeerkat release tags).

## DeepMeerkat 2.0 (legacy)

The **2.x** codebase is frozen at Git tag **`v2.0.0`** on branch **`v2.0`**. Use those only if you need the older application.

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

## PyPI and GitHub releases (maintainers)

### 1. Version bump

- Set `version` in `pyproject.toml` (for example `3.0.0`).
- Commit on `main`.

### 2. Tag and push

Create an annotated tag (example for **3.0.0**):

```bash
git tag -a v3.0.0 -m "DeepMeerkat 3.0.0"
git push origin v3.0.0
```

Pushing `v*` triggers:

- **`.github/workflows/publish.yml`** — sdist/wheel to **Test PyPI** then **PyPI** (requires repository secrets `TEST_PYPI_TOKEN` and `PYPI_TOKEN`).
- **`.github/workflows/build_installers.yml`** — builds **GUI** PyInstaller bundles on **Linux, Windows, and macOS** and uploads them to the **GitHub Release** for that tag (uses `GITHUB_TOKEN`).

If installer jobs fail (timeouts, size limits, or missing system libs), fix the workflow or build locally (below) and attach assets by hand on the release page.

### 3. GitHub Release assets

After the tag build, the release **v3.0.0** should list downloadable files similar to:

- `DeepMeerkat-v3.0.0-Windows-x64.exe`
- `DeepMeerkat-v3.0.0-macOS` (unsigned binary; see below)
- `DeepMeerkat-v3.0.0-Linux-x64.tar.gz`

Names follow the staging step in `build_installers.yml`.

### 4. Manual installer build (optional)

From the repository root, with the same Python you use for development:

```bash
pip install -e ".[ui]" pyinstaller
# or: pip install -e ".[ui,packaging]"
pyinstaller --noconfirm packaging/deepmeerkat-gui.spec
```

Outputs live under **`dist/`** (`deepmeerkat-gui` or `deepmeerkat-gui.exe`). A **CLI** one-file build is available via `packaging/deepmeerkat-cli.spec` (also large, includes PyTorch).

**macOS distribution:** CI produces a raw binary, not a signed **`.app`** or **`.dmg`**. For public distribution outside the lab, plan for **codesigning** and optionally **notarization** (Apple Developer Program), or ship via **pip** / conda instead.

**Linux:** The tarball contains a single executable built on a recent glibc (GitHub’s `ubuntu-latest`). Very old distributions may need a build on that target or a **pip** install.

## License

See `LICENSE`. Third-party models (MegaDetector) have their own terms; see the MegaDetector project documentation.
