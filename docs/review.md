# Review detections

After a run finishes, choose **Review detections** in the completion dialog, or use **File → Review results folder…** and pick a directory that contains `annotations.csv` (and a resolvable source video via `megadetector_results.json`, `fish_results.json`, or `parameters.csv`).

To **reload paths** from an old run into the main form (input video + output folder), use **File → Open result folder…**. After any completed run, **File → Reopen last results** jumps straight back into the review player for that output.

The review window shows the source video, a timeline scrubber, and a table of rows from `annotations.csv`. Bounding boxes on the video match the **filtered** table: change filters to focus on a class or confidence range.

## Layout

- **Splitter** — Drag the vertical bar between the video and the table to resize.
- **Label** — Restrict rows (and overlays) to one label, or **All**.
- **Min score** — Hide rows below this confidence (0.0–1.0). Missing scores are treated as **0.0**.

## Mouse

- **Scrub** the slider to move through the video.
- **Click a table row** to jump to that frame.
- **Prev detection / Next detection** — Jump to the previous or next frame that has at least one row in the **current filtered** table. Navigation **wraps** (e.g. from the last detection back to the first).

## Keyboard

| Key | Action |
|-----|--------|
| **←** **→** | Previous / next frame |
| **Home** | First frame |
| **End** | Last frame |
| **Space** | Start or stop playback (approx. video FPS, capped at 60 FPS) |

Playback stops when you scrub the slider, use arrow keys, jump to a detection, or reach the last frame.

## Files

- **Open result folder** opens the run directory in the system file manager (CSV, optional JSON, optional `detection_frames/` JPEGs).

If the source video path is missing or the file moved, the review window cannot open the player; keep outputs next to the original video or ensure `parameters.csv` lists the correct `source_video` path.

For files where the container reported **no frame count** or DeepMeerkat had to **scan** frames (see `video_frame_count_from_metadata` / `false` in `parameters.csv`), the player **does not use fast seek**; it decodes from the start of the file to reach the frame you chose. That avoids a black or frozen image when OpenCV’s `CAP_PROP_POS_FRAMES` is unreliable (some `.tlv` and similar). Optional **`video_fps_override`** in `parameters.csv` adjusts playback timing if you overrode FPS when running the job.
