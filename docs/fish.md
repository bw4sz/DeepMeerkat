# Community Fish Detector (underwater)

DeepMeerkat can run the **[Community Fish Detector](https://github.com/filippovarini/community-fish-detector)** — an RF-DETR Nano model trained on the [Community Fish Detection Dataset](https://lila.science/datasets/community-fish-detection-dataset) for a single class: **fish**. Use it for **underwater** or **benthic** video where MegaDetector’s terrestrial classes are a poor fit.

## Install extras

The implementation uses **RF-DETR** (`rfdetr` on PyPI), **supervision**, and **Pillow**:

```bash
pip install "deepmeerkat[fish]"
```

## Weights (automatic by default)

On first fish run, DeepMeerkat **downloads** the published RF-DETR Nano **`.pth`** (~116 MB) from the [Community Fish Detector release](https://github.com/filippovarini/community-fish-detector/releases/tag/cfd-2026.02.02-rf-detr-nano), verifies **SHA-256**, and caches it under the OS user cache (see `platformdirs` — typically `~/Library/Caches/deepmeerkat/fish/` on macOS). Later runs reuse the cache offline.

To use a **custom** checkpoint instead, pass `--fish-weights` / set **Weights** in the GUI.

## CLI

```bash
# Uses cached weights, or downloads once if missing
deepmeerkat run /path/to/video.avi --output ./out --mode fish
```

```bash
# Optional: point at a specific .pth file
deepmeerkat run /path/to/video.avi --output ./out --mode fish \
  --fish-weights /path/to/community-fish-detector-2026.02.02-rf-detr-nano-640.pth
```

Optional flags match the GUI: `--fish-confidence`, `--fish-resolution` (default **640**), `--fish-stride`, `--fish-target-fps`, `--fish-max-dimension`, `--fish-json` / `--no-fish-json`, `--fish-save-frames`.

## GUI

Choose **Community Fish Detector (underwater)** in **Mode**, then **Run**. Leave **Weights** empty to download automatically, or browse to a `.pth` file you manage yourself.

## Outputs

Fish runs write the same **`annotations.csv`** / **`parameters.csv`** as other modes, with label **`fish`**. **`fish_results.json`** holds per-frame summaries (when enabled). The **Review** window resolves the source video from `fish_results.json` or `parameters.csv`.

## License note

Model and dataset terms are described in the **Community Fish Detector** repository; training data mixes several licenses — see upstream docs before redistributing weights or outputs.
