# Migrating from DeepMeerkat 1.x to 3.0

- **Default pipeline**: DeepMeerkat 3.0 uses **MegaDetector** for generic animal / person / vehicle detection. The old TensorFlow “positive vs negative” SavedModel workflow is no longer required for that use case.
- **Classic motion mode**: OpenCV MOG2/KNN motion detection remains available as `--mode motion` or “Classic motion (OpenCV)” in the GUI.
- **Outputs**: Each run writes a folder per video under your chosen output directory, with `annotations.csv` and `parameters.csv`. MegaDetector runs also write `megadetector_results.json` by default.
- **Training crops**: Use motion mode with `--training` (or the GUI checkbox) to export motion crops similarly to legacy training mode.

For species-level identification after detection, consider tools such as SpeciesNet alongside MegaDetector outputs.
