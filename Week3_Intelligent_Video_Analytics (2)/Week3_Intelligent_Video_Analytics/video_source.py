"""
video_source.py
----------------
Resolves a video source (laptop webcam, Iriun mobile camera, an
uploaded/local video file, or an RTSP stream) into a cv2.VideoCapture
object, based on utils/config.py settings or explicit overrides.

This is the single place that knows how to open "whatever the user
picked", so app.py and streamlit_app.py both just call get_capture()
and don't need their own source-handling logic.
"""

import cv2

from utils import config


def get_capture(source_mode: str = None, file_path: str = None, rtsp_url: str = None):
    """
    Returns (cv2.VideoCapture, human_readable_label).

    source_mode : "webcam" | "iriun" | "file" | "rtsp"  (defaults to config.SOURCE_MODE)
    file_path   : path to a video file, used when source_mode == "file"
                  (defaults to config.VIDEO_PATH — set this to an uploaded
                  file's saved path when using the Streamlit upload option)
    rtsp_url    : stream URL, used when source_mode == "rtsp"
                  (defaults to config.RTSP_URL)
    """
    mode = (source_mode or config.SOURCE_MODE).lower()

    if mode == "webcam":
        cap = cv2.VideoCapture(config.WEBCAM_INDEX)
        label = f"Laptop Webcam (index {config.WEBCAM_INDEX})"

    elif mode == "iriun":
        cap = cv2.VideoCapture(config.IRIUN_INDEX)
        label = f"Iriun Mobile Camera (index {config.IRIUN_INDEX})"

    elif mode == "file":
        path = file_path or config.VIDEO_PATH
        cap = cv2.VideoCapture(path)
        label = f"Video File ({path})"

    elif mode == "rtsp":
        url = rtsp_url or config.RTSP_URL
        cap = cv2.VideoCapture(url)
        label = f"RTSP Stream ({url})"

    else:
        raise ValueError(
            f"Unknown SOURCE_MODE '{mode}'. Must be one of: webcam, iriun, file, rtsp."
        )

    if not cap.isOpened():
        cap.release()
        raise RuntimeError(
            f"Could not open video source: {label}\n"
            "Tips:\n"
            "  - webcam/iriun: run `python find_camera_index.py` to find the right index\n"
            "  - iriun: make sure the Iriun Webcam app is open on your phone AND the\n"
            "    Iriun desktop client is running and shows 'Connected'\n"
            "  - file: double-check the path exists\n"
            "  - rtsp: verify the URL, credentials, and that the camera is reachable"
        )

    return cap, label
