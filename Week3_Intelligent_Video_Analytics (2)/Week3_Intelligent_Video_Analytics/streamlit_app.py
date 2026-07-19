"""
streamlit_app.py
-----------------
A simple web-based control panel for the Intelligent Video Analytics
system. Lets you:

  - Pick a video source: Laptop Webcam, Iriun Mobile Camera,
    Upload a Video File, or an RTSP Stream URL
  - Pick a tracker: ByteTrack or BoT-SORT
  - Watch the annotated analytics feed live in the browser
  - Download the resulting output video and detection CSV log afterwards

Run:
    streamlit run streamlit_app.py
"""

import os
import tempfile
import time

import cv2
import numpy as np
import streamlit as st

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


st.set_page_config(page_title="Intelligent Video Analytics", layout="wide")
st.title("🎥 Intelligent Video Analytics — Control Panel")

# ---------------------------------------------------------------------
# Sidebar — source & settings
# ---------------------------------------------------------------------
st.sidebar.header("Video Source")

source_choice = st.sidebar.radio(
    "Choose input",
    ["Laptop Webcam", "Iriun Mobile Camera", "Upload Video File", "RTSP Stream"],
)

uploaded_file = None
rtsp_url_input = ""

if source_choice == "Upload Video File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload a video", type=["mp4", "avi", "mov", "mkv"]
    )
elif source_choice == "RTSP Stream":
    rtsp_url_input = st.sidebar.text_input("RTSP URL", value=config.RTSP_URL)
elif source_choice == "Iriun Mobile Camera":
    st.sidebar.info(
        "Make sure the Iriun Webcam app is running on your phone and the "
        "Iriun desktop client shows 'Connected' before starting."
    )
    iriun_index = st.sidebar.number_input(
        "Iriun camera index", min_value=0, max_value=10, value=config.IRIUN_INDEX
    )

st.sidebar.header("Tracker")
tracker_choice = st.sidebar.selectbox("Tracking algorithm", ["bytetrack", "botsort"])

st.sidebar.header("Detection")
conf_threshold = st.sidebar.slider("Confidence threshold", 0.05, 0.95, config.CONFIDENCE_THRESHOLD, 0.05)

start_button = st.sidebar.button("▶ Start Analytics", type="primary")
stop_button = st.sidebar.button("⏹ Stop")

frame_placeholder = st.empty()
stats_placeholder = st.empty()
download_placeholder = st.container()

if "running" not in st.session_state:
    st.session_state.running = False
if stop_button:
    st.session_state.running = False


def resolve_capture():
    """Map the sidebar choice to a (cv2.VideoCapture, label) pair."""
    if source_choice == "Laptop Webcam":
        return get_capture(source_mode="webcam")

    if source_choice == "Iriun Mobile Camera":
        config.IRIUN_INDEX = iriun_index
        return get_capture(source_mode="iriun")

    if source_choice == "Upload Video File":
        if uploaded_file is None:
            st.warning("Please upload a video file first.")
            st.stop()
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return get_capture(source_mode="file", file_path=tmp_path)

    if source_choice == "RTSP Stream":
        if not rtsp_url_input:
            st.warning("Please enter an RTSP URL first.")
            st.stop()
        return get_capture(source_mode="rtsp", rtsp_url=rtsp_url_input)

    raise ValueError("Unknown source choice")


if start_button:
    st.session_state.running = True

    cap, label = resolve_capture()
    st.info(f"Source: {label}  |  Tracker: {tracker_choice}")

    config.CONFIDENCE_THRESHOLD = conf_threshold

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 30

    ensure_dir(config.OUTPUT_VIDEO_PATH)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(config.OUTPUT_VIDEO_PATH, fourcc, fps_in, (frame_width, frame_height))

    tracker = ObjectTracker(config.MODEL_PATH, tracker_type=tracker_choice)
    line_counter = LineCounter(config.LINE_START, config.LINE_END)
    roi_manager = ROIManager(config.ROIS)
    trajectory_tracker = TrajectoryTracker()
    perf_monitor = PerformanceMonitor()
    dashboard = Dashboard()
    detection_logger = DetectionLogger(config.DETECTION_LOG_PATH) if config.SAVE_LOGS else None
    heatmap_gen = None

    frame_count = 0

    while st.session_state.running:
        ret, frame = cap.read()
        if not ret:
            st.success("Video finished (or stream ended).")
            break

        frame_count += 1
        perf_monitor.start_frame()

        if config.ENABLE_HEATMAP and heatmap_gen is None:
            heatmap_gen = HeatmapGenerator(frame.shape, radius=config.HEATMAP_RADIUS, decay=config.HEATMAP_DECAY)

        detections = tracker.update(frame)
        roi_manager.reset_frame()
        active_ids = set()
        confidences = []

        for box, tracker_id, class_id, confidence in zip(
            detections.xyxy, detections.tracker_id, detections.class_id, detections.confidence
        ):
            x1, y1, x2, y2 = box
            active_ids.add(tracker_id)
            confidences.append(confidence)
            class_name = tracker.class_name(class_id)

            line_counter.update(tracker_id, box)
            roi_zones = roi_manager.update(tracker_id, box)
            trajectory_tracker.update(tracker_id, box)
            direction = trajectory_tracker.annotate_direction(frame, tracker_id, box)

            draw_box(frame, box, tracker_id=tracker_id, label=class_name)
            draw_center_dot(frame, get_center(x1, y1, x2, y2))
            trajectory_tracker.draw(frame, tracker_id)

            if detection_logger:
                detection_logger.log(frame_count, tracker_id, class_name, confidence, box, roi_zones, direction)

        trajectory_tracker.cleanup(active_ids)

        if config.ENABLE_HEATMAP and heatmap_gen is not None:
            heatmap_gen.update(detections.xyxy)
            frame = heatmap_gen.overlay(frame, alpha=0.35)

        draw_line_counter(frame, config.LINE_START, config.LINE_END, color=config.LINE_COLOR)
        roi_manager.draw_all(frame)

        perf_monitor.end_frame()
        perf_stats = perf_monitor.snapshot()
        avg_conf = float(np.mean(confidences)) if confidences else 0.0

        dashboard.render(frame, {
            "fps": perf_stats["fps"],
            "current_objects": len(detections),
            "total_in": line_counter.in_count,
            "total_out": line_counter.out_count,
            "roi_counts": roi_manager.counts(),
            "avg_confidence": avg_conf,
            "processing_ms": perf_stats["processing_ms"],
            "cpu_percent": perf_stats["cpu_percent"],
            "memory_percent": perf_stats["memory_percent"],
        })

        writer.write(frame)
        frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

        stats_placeholder.markdown(
            f"**FPS:** {perf_stats['fps']:.1f}  |  "
            f"**Objects:** {len(detections)}  |  "
            f"**IN/OUT:** {line_counter.in_count}/{line_counter.out_count}  |  "
            f"**Avg Confidence:** {avg_conf*100:.1f}%  |  "
            f"**CPU:** {perf_stats['cpu_percent']:.1f}%  |  "
            f"**RAM:** {perf_stats['memory_percent']:.1f}%"
        )

        if not st.session_state.running:
            break

    cap.release()
    writer.release()
    if detection_logger:
        detection_logger.close()

    with download_placeholder:
        st.subheader("Downloads")
        if os.path.exists(config.OUTPUT_VIDEO_PATH):
            with open(config.OUTPUT_VIDEO_PATH, "rb") as f:
                st.download_button("⬇ Download annotated video", f, file_name="output.mp4")
        if os.path.exists(config.DETECTION_LOG_PATH):
            with open(config.DETECTION_LOG_PATH, "rb") as f:
                st.download_button("⬇ Download detection log (CSV)", f, file_name="detections.csv")
else:
    st.write("Choose a source in the sidebar and click **Start Analytics** to begin.")
