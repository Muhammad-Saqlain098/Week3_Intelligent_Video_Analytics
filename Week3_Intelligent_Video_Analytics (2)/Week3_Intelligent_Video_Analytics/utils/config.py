"""
config.py
---------
Central configuration file for the Intelligent Video Analytics project.
Every tunable value lives here so the rest of the codebase never
hard-codes a number — change behaviour by editing this file only.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")          # YOLO weights
VIDEO_PATH = os.path.join(BASE_DIR, "videos", "input.mp4")       # Source video
OUTPUT_VIDEO_PATH = os.path.join(BASE_DIR, "outputs", "output.mp4")
DETECTION_LOG_PATH = os.path.join(BASE_DIR, "outputs", "detections.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "outputs", "screenshots")

# ---------------------------------------------------------------------------
# Video Source
# ---------------------------------------------------------------------------
# SOURCE_MODE controls where frames come from. One of:
#   "webcam"  -> built-in laptop camera (index = WEBCAM_INDEX)
#   "iriun"   -> phone camera via the Iriun Webcam app (index = IRIUN_INDEX)
#   "file"    -> a video file on disk (path = VIDEO_PATH, or an uploaded file)
#   "rtsp"    -> a network camera / RTSP stream (url = RTSP_URL)
SOURCE_MODE = "file"

WEBCAM_INDEX = 0          # laptop's built-in webcam is almost always 0

# Iriun Webcam registers itself as a regular OpenCV camera device, just at
# a different index because it's installed *after* your laptop's own
# camera. On most Windows/Linux laptops with one built-in camera, Iriun
# shows up at index 1. If you have more than one physical camera (or a
# virtual camera like OBS already installed), it may be at index 2 instead.
# Simplest way to find yours: run `python find_camera_index.py`.
IRIUN_INDEX = 1

RTSP_URL = "rtsp://username:password@camera-ip:554/stream"

# Backwards-compat flag (kept so older scripts referencing USE_WEBCAM still work)
USE_WEBCAM = SOURCE_MODE == "webcam"

# ---------------------------------------------------------------------------
# Detection / Tracking
# ---------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.35
IOU_THRESHOLD = 0.45
CLASSES_TO_DETECT = None      # None = detect all classes, or e.g. [0, 2] for person/car

# TRACKER_TYPE selects which multi-object tracker ultralytics uses under
# the hood. Both ship built-in with the `ultralytics` package as ready-made
# YAML configs — no extra install needed. This is what Assignment 2
# (Tracking Experiments) switches between.
#   "bytetrack" -> fast, motion-only association (bytetrack.yaml)
#   "botsort"   -> adds appearance (Re-ID) + camera-motion compensation (botsort.yaml)
TRACKER_TYPE = "bytetrack"

# Legacy ByteTrack parameters (used only by the standalone supervision-based
# tracker in tracker_supervision.py, kept for reference/comparison)
TRACK_ACTIVATION_THRESHOLD = 0.25
LOST_TRACK_BUFFER = 30
MINIMUM_MATCHING_THRESHOLD = 0.8
FRAME_RATE = 30

# ---------------------------------------------------------------------------
# Virtual Line Counter (IN / OUT)
# ---------------------------------------------------------------------------
# Line defined by two points (x1, y1) -> (x2, y2)
LINE_START = (100, 400)
LINE_END = (900, 400)
LINE_COLOR = (0, 0, 255)
LINE_THICKNESS = 2

# ---------------------------------------------------------------------------
# Region of Interest (ROI)
# ---------------------------------------------------------------------------
# Multiple ROIs supported. Each ROI is (name, x1, y1, x2, y2, color)
ROIS = [
    {"name": "Warehouse", "x1": 200, "y1": 100, "x2": 700, "y2": 500, "color": (255, 0, 255)},
]

# ---------------------------------------------------------------------------
# Trajectory
# ---------------------------------------------------------------------------
TRAJECTORY_MAX_LENGTH = 30       # number of past points to keep per object
TRAJECTORY_COLOR = (0, 255, 255)
TRAJECTORY_THICKNESS = 2

# ---------------------------------------------------------------------------
# Dashboard / UI
# ---------------------------------------------------------------------------
FONT = "FONT_HERSHEY_SIMPLEX"
FONT_SCALE = 0.7
FONT_THICKNESS = 2
DASHBOARD_BG_COLOR = (30, 30, 30)
DASHBOARD_TEXT_COLOR = (255, 255, 255)
DASHBOARD_ALPHA = 0.55           # transparency of dashboard panel

# ---------------------------------------------------------------------------
# Heatmap (bonus)
# ---------------------------------------------------------------------------
ENABLE_HEATMAP = True
HEATMAP_RADIUS = 15
HEATMAP_DECAY = 0.98              # multiplied each frame so old heat fades
HEATMAP_COLORMAP = "COLORMAP_JET"

# ---------------------------------------------------------------------------
# Logging / Output
# ---------------------------------------------------------------------------
SAVE_VIDEO = True
SAVE_LOGS = True
DISPLAY_WINDOW = True             # set False when running headless / on a server
