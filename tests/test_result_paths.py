import json
from pathlib import Path

from deepmeerkat.result_paths import (
    load_annotation_rows,
    paths_from_result_run_folder,
    read_parameters_csv,
    resolve_source_video,
)


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


def test_resolve_from_fish_json(tmp_path: Path) -> None:
    vid = tmp_path / "u.avi"
    vid.write_bytes(b"x")
    js = tmp_path / "fish_results.json"
    js.write_text(json.dumps({"video": str(vid)}), encoding="utf-8")
    assert resolve_source_video(tmp_path) == vid


def test_paths_from_result_run_folder(tmp_path: Path) -> None:
    run = tmp_path / "garcon_test"
    run.mkdir()
    (run / "annotations.csv").write_text("frame,clock,x,y,h,w,label,score\n", encoding="utf-8")
    vid = tmp_path / "source.avi"
    vid.write_bytes(b"x")
    (run / "parameters.csv").write_text(f"source_video,{vid}\n", encoding="utf-8")
    v, parent = paths_from_result_run_folder(run)
    assert v == vid
    assert parent == tmp_path


def test_load_annotation_rows(tmp_path: Path) -> None:
    p = tmp_path / "annotations.csv"
    p.write_text(
        "frame,clock,x,y,h,w,label,score\n1,0:00:00,0,0,10,10,animal,0.9\n",
        encoding="utf-8",
    )
    rows = load_annotation_rows(p)
    assert len(rows) == 1
    assert rows[0]["label"] == "animal"
