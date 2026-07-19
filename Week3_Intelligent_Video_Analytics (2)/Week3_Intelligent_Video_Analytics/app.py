"""
app.py
------
Main application entry point for the Week 3 Intelligent Video Analytics
project.

Pipeline:
    Video -> YOLO Detection -> Tracking (ByteTrack/BoT-SORT) -> Object IDs
          -> Line Counter (IN/OUT) -> ROI Monitoring
          -> Trajectory + Direction -> Heatmap
          -> Analytics Dashboard -> Detection Logs -> Output Video

Video source options (Feature: Method 4 - Mobile Camera support):
    --source webcam   Laptop's built-in camera (utils/config.py WEBCAM_INDEX)
    --source iriun    Phone camera via the Iriun Webcam app (IRIUN_INDEX)
    --source file     A video file — pass its path with --video
    --source rtsp     A network camera stream — pass its URL with --rtsp-url

Tracker options (Assignment 2: Tracking Experiments):
    --tracker bytetrack   Fast, motion-only association (default)
    --tracker botsort     Adds appearance Re-ID + camera-motion compensation

Run:
    python app.py                                   # uses utils/config.py defaults
    python app.py --source webcam                    # laptop camera
    python app.py --source iriun                      # phone via Iriun Webcam
    python app.py --source file --video videos/input.mp4
    python app.py --source rtsp --rtsp-url rtsp://...
    python app.py --tracker botsort
"""

import os
import argparse
import cv2
import numpy as np

from utils import config
from utils.drawing import draw_box, draw_center_dot, draw_line_counter
from utils.helpers import ensure_dir, get_center

from tracker import ObjectTracker
from counter import LineCounter
from roi import ROIManager
from trajectory import TrajectoryTracker
from performance import PerformanceMonitor
from logger import DetectionLogger
from dashboard import Dashboard
from heatmap import HeatmapGenerator
from video_source import get_capture


def parse_args():
    parser = argparse.ArgumentParser(description="Intelligent Video Analytics")
    parser.add_argument(
        "--source", choices=["webcam", "iriun", "file", "rtsp"], default=None,
        help="Video source. Defaults to utils/config.py SOURCE_MODE.",
    )
    parser.add_argument("--video", default=None, help="Path to a video file (used with --source file)")
    parser.add_argument("--rtsp-url", default=None, help="RTSP stream URL (used with --source rtsp)")
    parser.add_argument(
        "--tracker", choices=["bytetrack", "botsort"], default=None,
        help="Tracking algorithm. Defaults to utils/config.py TRACKER_TYPE.",
    )
    parser.add_argument("--no-display", action="store_true", help="Run headless (no preview window)")
    return parser.parse_args()


def main():
    args = parse_args()

    # ---------------------------------------------------------------
    # Setup
    # ---------------------------------------------------------------
    cap, source_label = get_capture(
        source_mode=args.source, file_path=args.video, rtsp_url=args.rtsp_url
    )
    print(f"Video source: {source_label}")

    if args.no_display:
        config.DISPLAY_WINDOW = False

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 30

    writer = None
    if config.SAVE_VIDEO:
        ensure_dir(config.OUTPUT_VIDEO_PATH)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            config.OUTPUT_VIDEO_PATH, fourcc, fps_in, (frame_width, frame_height)
        )

    tracker = ObjectTracker(config.MODEL_PATH, tracker_type=args.tracker)
    print(f"Tracker: {tracker.tracker_type}")
    line_counter = LineCounter(config.LINE_START, config.LINE_END)
    roi_manager = ROIManager(config.ROIS)
    trajectory_tracker = TrajectoryTracker()
    perf_monitor = PerformanceMonitor()
    dashboard = Dashboard()

    detection_logger = DetectionLogger(config.DETECTION_LOG_PATH) if config.SAVE_LOGS else None
    heatmap_gen = None

    frame_count = 0

    # ---------------------------------------------------------------
    # Main loop
    # ---------------------------------------------------------------
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        perf_monitor.start_frame()

        if config.ENABLE_HEATMAP and heatmap_gen is None:
            heatmap_gen = HeatmapGenerator(
                frame.shape,
                radius=config.HEATMAP_RADIUS,
                decay=config.HEATMAP_DECAY,
            )

        # --- Detection + Tracking -----------------------------------
        detections = tracker.update(frame)

        roi_manager.reset_frame()
        active_ids = set()
        confidences = []

        # --- Per-object processing -----------------------------------
        for box, tracker_id, class_id, confidence in zip(
            detections.xyxy,
            detections.tracker_id,
            detections.class_id,
            detections.confidence,
        ):
            x1, y1, x2, y2 = box
            active_ids.add(tracker_id)
            confidences.append(confidence)
            class_name = tracker.class_name(class_id)

            # Line counter
            event = line_counter.update(tracker_id, box)

            # ROI monitoring
            roi_zones = roi_manager.update(tracker_id, box)

            # Trajectory + direction
            trajectory_tracker.update(tracker_id, box)
            direction = trajectory_tracker.annotate_direction(frame, tracker_id, box)

            # Drawing
            draw_box(frame, box, tracker_id=tracker_id, label=class_name)
            draw_center_dot(frame, get_center(x1, y1, x2, y2))
            trajectory_tracker.draw(frame, tracker_id)

            # Logging
            if detection_logger:
                detection_logger.log(
                    frame_count, tracker_id, class_name, confidence,
                    box, roi_zones=roi_zones, direction=direction,
                )

        trajectory_tracker.cleanup(active_ids)

        # --- Heatmap ---------------------------------------------------
        if config.ENABLE_HEATMAP and heatmap_gen is not None:
            heatmap_gen.update(detections.xyxy)
            frame = heatmap_gen.overlay(frame, alpha=0.35)

        # --- Static overlays --------------------------------------------
        draw_line_counter(frame, config.LINE_START, config.LINE_END, color=config.LINE_COLOR)
        roi_manager.draw_all(frame)

        # --- Performance ------------------------------------------------
        perf_monitor.end_frame()
        perf_stats = perf_monitor.snapshot()

        avg_conf = float(np.mean(confidences)) if confidences else 0.0

        dashboard.render(
            frame,
            {
                "fps": perf_stats["fps"],
                "current_objects": len(detections),
                "total_in": line_counter.in_count,
                "total_out": line_counter.out_count,
                "roi_counts": roi_manager.counts(),
                "avg_confidence": avg_conf,
                "processing_ms": perf_stats["processing_ms"],
                "cpu_percent": perf_stats["cpu_percent"],
                "memory_percent": perf_stats["memory_percent"],
            },
        )

        # --- Output -------------------------------------------------------
        if writer is not None:
            writer.write(frame)

        if config.DISPLAY_WINDOW:
            cv2.imshow("Intelligent Video Analytics - Week 3", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                ensure_dir(config.SCREENSHOT_DIR)
                screenshot_path = os.path.join(
                    config.SCREENSHOT_DIR, f"screenshot_{frame_count}.png"
                )
                cv2.imwrite(screenshot_path, frame)
                print(f"Saved screenshot: {screenshot_path}")

        if frame_count % 30 == 0:
            print(
                f"Frame {frame_count} | FPS {perf_stats['fps']:.1f} | "
                f"Objects {len(detections)} | IN {line_counter.in_count} | "
                f"OUT {line_counter.out_count}"
            )

    # ---------------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------------
    cap.release()
    if writer is not None:
        writer.release()
    if detection_logger:
        detection_logger.close()
    cv2.destroyAllWindows()

    print("\n=== Run Summary ===")
    print(f"Total Frames Processed : {frame_count}")
    print(f"Total IN               : {line_counter.in_count}")
    print(f"Total OUT              : {line_counter.out_count}")
    print(f"Output video           : {config.OUTPUT_VIDEO_PATH}")
    print(f"Detection log          : {config.DETECTION_LOG_PATH}")


if __name__ == "__main__":
    main()
