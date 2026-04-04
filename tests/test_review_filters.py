from deepmeerkat.ui.review_filters import (
    filter_annotation_rows,
    sorted_unique_frames,
    unique_labels,
)


def _rows() -> list[dict[str, str]]:
    return [
        {"frame": "1", "label": "animal", "score": "0.9"},
        {"frame": "1", "label": "person", "score": "0.3"},
        {"frame": "5", "label": "animal", "score": "0.2"},
        {"frame": "bad", "label": "x", "score": "1"},
    ]


def test_filter_by_label_and_score() -> None:
    r = _rows()
    out = filter_annotation_rows(r, label="animal", min_score=0.25)
    assert len(out) == 1
    assert out[0]["frame"] == "1"


def test_filter_all_labels() -> None:
    r = _rows()
    out = filter_annotation_rows(r, label=None, min_score=0.0)
    assert len(out) == 3


def test_sorted_unique_frames() -> None:
    r = _rows()
    assert sorted_unique_frames(r) == [1, 5]


def test_unique_labels() -> None:
    assert unique_labels(_rows()) == ["animal", "person"]
