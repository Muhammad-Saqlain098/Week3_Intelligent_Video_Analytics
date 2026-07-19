"""
helpers.py
----------
Small, reusable helper functions shared across modules.
"""

import os
import time


def get_center(x1, y1, x2, y2):
    """Return the integer center point (cx, cy) of a bounding box."""
    cx = int((x1 + x2) / 2)
    cy = int((y1 + y2) / 2)
    return cx, cy


def ensure_dir(path: str):
    """Create the parent directory of `path` if it doesn't already exist."""
    directory = path if os.path.isdir(path) or "." not in os.path.basename(path) else os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


class FPSMeter:
    """Simple exponential-moving-average FPS counter."""

    def __init__(self, smoothing: float = 0.9):
        self._smoothing = smoothing
        self._last_time = None
        self._fps = 0.0

    def tick(self) -> float:
        now = time.time()
        if self._last_time is not None:
            instant_fps = 1.0 / max(now - self._last_time, 1e-6)
            self._fps = (
                self._fps * self._smoothing + instant_fps * (1 - self._smoothing)
                if self._fps > 0
                else instant_fps
            )
        self._last_time = now
        return self._fps

    @property
    def fps(self) -> float:
        return self._fps


def format_seconds(seconds: float) -> str:
    """Format a duration in seconds as HH:MM:SS."""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
