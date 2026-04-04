import json
from pathlib import Path

from deepmeerkat.export import write_annotations_csv, write_json, write_parameters_csv


def test_write_parameters_csv(tmp_path: Path) -> None:
    p = tmp_path / "p.csv"
    write_parameters_csv(p, {"a": 1, "b": "x"})
    text = p.read_text(encoding="utf-8")
    assert "a" in text and "b" in text


def test_write_json(tmp_path: Path) -> None:
    p = tmp_path / "j.json"
    write_json(p, {"k": [1, 2]})
    assert json.loads(p.read_text(encoding="utf-8")) == {"k": [1, 2]}


def test_write_annotations_csv_empty(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    write_annotations_csv(p, [])
    assert "frame" in p.read_text(encoding="utf-8")
