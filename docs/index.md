# DeepMeerkat

**DeepMeerkat 3.x** processes ecological camera videos in several modes:

- **MegaDetector (default)** — animal, person, and vehicle bounding boxes per frame.
- **Community Fish Detector** — single-class **fish** detection for underwater / benthic video ([RF-DETR](https://github.com/filippovarini/community-fish-detector)).
- **Classic motion (OpenCV)** — background-subtraction motion regions, compatible with legacy workflows.

Outputs include `annotations.csv`, run parameters, and optional JSON. A desktop app (PySide6) and CLI are provided.

[Getting started](getting-started.md) · [Fish detector](fish.md) · [Review window](review.md) · [GitHub](https://github.com/bw4sz/DeepMeerkat)
