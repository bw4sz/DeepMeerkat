"""MegaDetector category codes to human-readable labels."""

MD_LABELS = {"1": "animal", "2": "person", "3": "vehicle"}


def category_label(category: str | int) -> str:
    key = str(category)
    return MD_LABELS.get(key, key)
