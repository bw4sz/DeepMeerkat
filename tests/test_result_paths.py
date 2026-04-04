import json
from pathlib import Path

from deepmeerkat.result_paths import load_annotation_rows, read_parameters_csv, resolve_source_video


def test_read_parameters_csv(tmp_path: Path) -> None:
    p = tmp_path / "parameters.csv"
    p.write_text("mode,megadetector\nsource_video,/tmp/a.mp4\n", encoding="utf-8")
    d = read_parameters_csv(p)
    assert d.get("mode") == "megadetector"
    assert d.get("source_video") == "/tmp/a.mp4"


def test_resolve_from_json(tmp_path: Path) -> None:
    vid = tmp_path / "clip.mp4"
    vid.write_bytes(b"not a real video")
    js = tmp_path / "megadetector_results.json"
    js.write_text(json.dumps({"video": str(vid)}), encoding="utf-8")
    assert resolve_source_video(tmp_path) == vid


def test_load_annotation_rows(tmp_path: Path) -> None:
    p = tmp_path / "annotations.csv"
    p.write_text(
        "frame,clock,x,y,h,w,label,score\n1,0:00:00,0,0,10,10,animal,0.9\n",
        encoding="utf-8",
    )
    rows = load_annotation_rows(p)
    assert len(rows) == 1
    assert rows[0]["label"] == "animal"
