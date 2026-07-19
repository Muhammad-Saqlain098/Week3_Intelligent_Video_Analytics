"""
tracking_experiments.py
------------------------
Assignment 2: Tracking Experiments.

Runs four experiments against a fixed test video and writes the
results to outputs/tracking_experiments_results.csv plus a printed
summary table:

  Experiment 1: ByteTrack               — baseline tracker performance
  Experiment 2: BoT-SORT                — compare vs. ByteTrack
  Experiment 3: Confidence thresholds    — impact of conf on detections/FPS
  Experiment 4: Video resolutions        — impact of resolution on FPS

Run:
    python tracking_experiments.py --video videos/input.mp4
"""

import argparse
import csv
import time

import cv2

from utils import config
from utils.helpers import ensure_dir
from tracker import ObjectTracker


def run_single_pass(video_path, tracker_type, conf_threshold, resize_to=None, max_frames=300):
    """
    Processes up to `max_frames` frames of `video_path` with the given
    tracker + confidence threshold (and optional resize), returning a
    dict of summary metrics.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    original_conf = config.CONFIDENCE_THRESHOLD
    config.CONFIDENCE_THRESHOLD = conf_threshold
    tracker = ObjectTracker(config.MODEL_PATH, tracker_type=tracker_type)

    frame_count = 0
    total_detections = 0
    unique_ids = set()
    id_switch_estimate = 0
    confidences = []
    start_time = time.time()

    prev_ids = set()

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if resize_to is not None:
            frame = cv2.resize(frame, resize_to)

        detections = tracker.update(frame)
        frame_count += 1
        total_detections += len(detections)

        current_ids = set(int(tid) for tid in detections.tracker_id)
        unique_ids.update(current_ids)

        # crude proxy for ID instability: IDs that vanish and later a
        # brand-new ID appears close in count to what vanished
        vanished = prev_ids - current_ids
        appeared = current_ids - prev_ids
        id_switch_estimate += min(len(vanished), len(appeared))
        prev_ids = current_ids

        confidences.extend(float(c) for c in detections.confidence)

    elapsed = time.time() - start_time
    cap.release()
    config.CONFIDENCE_THRESHOLD = original_conf

    fps = frame_count / elapsed if elapsed > 0 else 0.0
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    return {
        "frames_processed": frame_count,
        "elapsed_seconds": round(elapsed, 2),
        "fps": round(fps, 2),
        "total_detections": total_detections,
        "avg_detections_per_frame": round(total_detections / frame_count, 2) if frame_count else 0,
        "unique_track_ids": len(unique_ids),
        "estimated_id_switches": id_switch_estimate,
        "avg_confidence": round(avg_conf, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Week 3 Assignment 2: Tracking Experiments")
    parser.add_argument("--video", default=config.VIDEO_PATH, help="Path to test video")
    parser.add_argument("--max-frames", type=int, default=300, help="Frames to process per experiment")
    args = parser.parse_args()

    results = []

    # --- Experiment 1 & 2: ByteTrack vs BoT-SORT -----------------------
    print("\n=== Experiment 1: ByteTrack ===")
    r1 = run_single_pass(args.video, "bytetrack", config.CONFIDENCE_THRESHOLD, max_frames=args.max_frames)
    r1.update({"experiment": "1_tracker_comparison", "tracker": "bytetrack",
               "confidence": config.CONFIDENCE_THRESHOLD, "resolution": "original"})
    results.append(r1)
    print(r1)

    print("\n=== Experiment 2: BoT-SORT ===")
    r2 = run_single_pass(args.video, "botsort", config.CONFIDENCE_THRESHOLD, max_frames=args.max_frames)
    r2.update({"experiment": "2_tracker_comparison", "tracker": "botsort",
               "confidence": config.CONFIDENCE_THRESHOLD, "resolution": "original"})
    results.append(r2)
    print(r2)

    # --- Experiment 3: Confidence thresholds ---------------------------
    print("\n=== Experiment 3: Confidence Thresholds (ByteTrack) ===")
    for conf in [0.15, 0.25, 0.35, 0.5, 0.7]:
        r = run_single_pass(args.video, "bytetrack", conf, max_frames=args.max_frames)
        r.update({"experiment": "3_confidence_threshold", "tracker": "bytetrack",
                   "confidence": conf, "resolution": "original"})
        results.append(r)
        print(f"conf={conf} -> {r}")

    # --- Experiment 4: Resolutions -------------------------------------
    print("\n=== Experiment 4: Video Resolutions (ByteTrack) ===")
    for resolution in [(320, 240), (640, 480), (1280, 720)]:
        r = run_single_pass(
            args.video, "bytetrack", config.CONFIDENCE_THRESHOLD,
            resize_to=resolution, max_frames=args.max_frames,
        )
        r.update({"experiment": "4_resolution", "tracker": "bytetrack",
                   "confidence": config.CONFIDENCE_THRESHOLD, "resolution": f"{resolution[0]}x{resolution[1]}"})
        results.append(r)
        print(f"resolution={resolution} -> {r}")

    # --- Save results ----------------------------------------------------
    out_path = "outputs/tracking_experiments_results.csv"
    ensure_dir(out_path)
    fieldnames = [
        "experiment", "tracker", "confidence", "resolution",
        "frames_processed", "elapsed_seconds", "fps", "total_detections",
        "avg_detections_per_frame", "unique_track_ids",
        "estimated_id_switches", "avg_confidence",
    ]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"\nAll experiment results saved to: {out_path}")


if __name__ == "__main__":
    main()
