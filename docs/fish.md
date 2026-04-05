# Community Fish Detector (underwater)

DeepMeerkat can run the **[Community Fish Detector](https://github.com/filippovarini/community-fish-detector)** — an RF-DETR Nano model trained on the [Community Fish Detection Dataset](https://lila.science/datasets/community-fish-detection-dataset) for a single class: **fish**. Use it for **underwater** or **benthic** video where MegaDetector’s terrestrial classes are a poor fit.

## Install extras

The implementation uses **RF-DETR** (`rfdetr` on PyPI), **supervision**, and **Pillow**:

```bash
pip install "deepmeerkat[fish]"
```

## Download weights

Download the published **`.pth`** checkpoint (for example **RF-DETR Nano @ 640**) from the project’s **[GitHub Releases](https://github.com/filippovarini/community-fish-detector/releases)** and note the path on disk.

## CLI

```bash
deepmeerkat run /path/to/video.avi --output ./out --mode fish \
  --fish-weights /path/to/community-fish-detector-2026.02.02-rf-detr-nano-640.pth
```

Optional flags match the GUI: `--fish-confidence`, `--fish-resolution` (default **640**), `--fish-stride`, `--fish-target-fps`, `--fish-max-dimension`, `--fish-json` / `--no-fish-json`, `--fish-save-frames`.

## GUI

Choose **Community Fish Detector (underwater)** in **Mode**, set **Weights (.pth)** to your checkpoint file, then **Run**.

## Outputs

Fish runs write the same **`annotations.csv`** / **`parameters.csv`** as other modes, with label **`fish`**. **`fish_results.json`** holds per-frame summaries (when enabled). The **Review** window resolves the source video from `fish_results.json` or `parameters.csv`.

## License note

Model and dataset terms are described in the **Community Fish Detector** repository; training data mixes several licenses — see upstream docs before redistributing weights or outputs.
