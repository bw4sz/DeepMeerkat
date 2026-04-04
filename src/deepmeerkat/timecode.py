"""Frame index ↔ clock time helpers."""


def frame_to_clock_str(frame_index: int, fps: float) -> str:
    """Return H:MM:SS clock string for 1-based frame display (matches legacy style)."""
    if fps <= 0:
        fps = 30.0
    # Legacy used frame_count directly in time_est = (frame_count/fps)/3600
    t = (frame_index / fps) % 86400.0
    hours = int(t // 3600)
    minutes = int((t % 3600) // 60)
    seconds = int(t % 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"
