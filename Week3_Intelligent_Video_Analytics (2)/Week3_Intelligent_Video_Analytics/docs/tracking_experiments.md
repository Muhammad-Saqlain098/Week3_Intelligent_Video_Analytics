# Tracking Experiments — Assignment 2

This document describes the four required tracking experiments and how
to reproduce them. The runnable script is `tracking_experiments.py` at
the project root; it writes raw numeric results to
`outputs/tracking_experiments_results.csv`.

## How to Run

```bash
python tracking_experiments.py --video videos/input.mp4 --max-frames 300
```

This processes the first 300 frames of the given video under each
experimental condition below and prints a summary, then saves every
result row to `outputs/tracking_experiments_results.csv`.

## Experiment 1 — ByteTrack (Baseline)

Runs the full pipeline with `tracker="bytetrack"` at the default
confidence threshold and original video resolution. This is the
baseline every other experiment is compared against.

**What to look for**: FPS, total detections, unique track IDs
generated, and estimated ID switches.

## Experiment 2 — BoT-SORT

Identical setup to Experiment 1, but with `tracker="botsort"`.

**Expected observations**: BoT-SORT typically shows a lower FPS than
ByteTrack (extra appearance/Re-ID + camera-motion-compensation cost),
but fewer estimated ID switches in scenes with occlusion or camera
movement, since it uses more information to re-associate tracks.

**Comparison**: Directly diff the Experiment 1 vs. Experiment 2 rows in
`outputs/tracking_experiments_results.csv` — same video, same
confidence threshold, same resolution, only the tracker changes.

## Experiment 3 — Confidence Thresholds

Runs ByteTrack across five confidence thresholds: 0.15, 0.25, 0.35,
0.5, and 0.7.

**Expected observations**:
- Lower thresholds → more (and noisier) detections per frame, which
  can increase false-positive tracks but also catch more genuinely
  faint/occluded objects.
- Higher thresholds → fewer, higher-quality detections, but real
  objects with borderline confidence may be missed entirely, causing
  their tracks to break and restart with a new ID once confidence
  recovers.
- FPS is largely unaffected by the threshold itself (it's a filter
  applied after inference), so this experiment mainly reveals a
  detection-quality trade-off rather than a speed trade-off.

## Experiment 4 — Video Resolutions

Runs ByteTrack at three resolutions: 320×240, 640×480, and 1280×720
(frames are resized before inference).

**Expected observations**: FPS decreases as resolution increases, since
YOLOv8's inference cost scales with input pixel count. Smaller objects
may be missed entirely at 320×240 due to insufficient detail, which can
also reduce the count of unique tracked objects relative to the higher
resolutions.

## Recording Your Own Results

After running the script on your own test video, open
`outputs/tracking_experiments_results.csv` and summarize the key
numbers (FPS, avg detections/frame, estimated ID switches) into a
table like this for your submission:

| Experiment | Tracker | Confidence | Resolution | FPS | Avg Det/Frame | Est. ID Switches |
|---|---|---|---|---|---|---|
| 1 | bytetrack | default | original | — | — | — |
| 2 | botsort | default | original | — | — | — |
| 3a | bytetrack | 0.15 | original | — | — | — |
| 3b | bytetrack | 0.25 | original | — | — | — |
| 3c | bytetrack | 0.35 | original | — | — | — |
| 3d | bytetrack | 0.50 | original | — | — | — |
| 3e | bytetrack | 0.70 | original | — | — | — |
| 4a | bytetrack | default | 320x240 | — | — | — |
| 4b | bytetrack | default | 640x480 | — | — | — |
| 4c | bytetrack | default | 1280x720 | — | — | — |

Fill in the dashes with the actual values from your CSV output before
submitting.
