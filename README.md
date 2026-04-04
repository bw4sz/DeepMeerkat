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

## Downloads (GUI installers)

[GitHub Releases](https://github.com/bw4sz/DeepMeerkat/releases/latest) attach **Windows** and **macOS** GUI builds when CI succeeds. There is **no Linux `.tar.gz` or AppImage**: bundled PyTorch pushes past **GitHub’s 2 GiB per-file limit**, so **Linux is supported only via PyPI** (and CLI from the same environment).

**Linux**

```bash
pip install "deepmeerkat[ui]"
deepmeerkat-gui
```

**Windows** — run the downloaded `.exe`.

**macOS** — the release file is named like **`DeepMeerkat-v3.0.0-macOS`** (version in the name). It is **not** a `.dmg` or `.app`; it is a **single unsigned executable**. Use **Terminal** (double-click usually does not launch the GUI):

1. Open **Terminal**.
2. `cd` to the folder where you saved the file (often `~/Downloads`).
3. Make it executable once: `chmod +x DeepMeerkat-v3.0.0-macOS` (match the filename from the release).
4. Run it: `./DeepMeerkat-v3.0.0-macOS`

Copy-paste example (adjust filename if your version differs):

```bash
cd ~/Downloads
chmod +x DeepMeerkat-v3.0.0-macOS
./DeepMeerkat-v3.0.0-macOS
```

If macOS blocks it (**unidentified developer**): **System Settings → Privacy & Security** → find the prompt → **Open Anyway**; or in **Finder**, **Control-click** the file → **Open** → confirm.

Easier on Mac: **`pip install "deepmeerkat[ui]"`** then **`deepmeerkat-gui`** (same app, no unsigned binary).

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
- **`.github/workflows/build_installers.yml`** — builds **GUI** PyInstaller bundles for **Windows and macOS** only; uploads to the **GitHub Release** (uses `GITHUB_TOKEN`). **No Linux binary** (see **Downloads** above).

If installer jobs fail (timeouts, size limits, or missing system libs), fix the workflow or build locally (below) and attach assets by hand on the release page.

### 3. GitHub Release assets

After the tag build, the release **v3.0.0** should list downloadable files similar to:

- `DeepMeerkat-v3.0.0-Windows-x64.exe`
- `DeepMeerkat-v3.0.0-macOS` (unsigned binary; see below)

Names follow `build_installers.yml`.

### 4. Manual installer build (optional)

From the repository root, with the same Python you use for development:

```bash
pip install -e ".[ui]" pyinstaller
# or: pip install -e ".[ui,packaging]"
pyinstaller --noconfirm packaging/deepmeerkat-gui.spec
```

Outputs live under **`dist/`** (`deepmeerkat-gui` or `deepmeerkat-gui.exe`). A **CLI** one-file build is available via `packaging/deepmeerkat-cli.spec` (also large, includes PyTorch).

**macOS distribution:** CI produces a raw binary, not a signed **`.app`** or **`.dmg`**. For public distribution outside the lab, plan for **codesigning** and optionally **notarization** (Apple Developer Program), or ship via **pip** / conda instead.

**Linux:** We do **not** publish a release binary. Use **`pip install "deepmeerkat[ui]"`**. Advanced users can run PyInstaller locally; the bundle is typically too large for GitHub Releases.

## License

See `LICENSE`. Third-party models (MegaDetector) have their own terms; see the MegaDetector project documentation.
