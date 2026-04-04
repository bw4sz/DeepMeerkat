from deepmeerkat.timecode import frame_to_clock_str


def test_frame_to_clock_str() -> None:
    s = frame_to_clock_str(150, 30.0)
    assert s == "0:00:05"
