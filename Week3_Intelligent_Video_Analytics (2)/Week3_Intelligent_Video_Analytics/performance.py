"""
performance.py
--------------
Tracks real-time system performance: FPS, per-frame processing time,
CPU usage, and memory usage. Uses psutil for system stats.
"""

import time
import psutil

from utils.helpers import FPSMeter


class PerformanceMonitor:
    def __init__(self):
        self._fps_meter = FPSMeter()
        self._frame_start = None
        self.last_processing_ms = 0.0

    def start_frame(self):
        """Call at the very start of each frame's processing."""
        self._frame_start = time.time()

    def end_frame(self):
        """Call after all processing for the frame is done."""
        if self._frame_start is not None:
            self.last_processing_ms = (time.time() - self._frame_start) * 1000
        self._fps_meter.tick()

    @property
    def fps(self) -> float:
        return self._fps_meter.fps

    @staticmethod
    def cpu_usage() -> float:
        return psutil.cpu_percent()

    @staticmethod
    def memory_usage_percent() -> float:
        return psutil.virtual_memory().percent

    @staticmethod
    def memory_usage_gb() -> float:
        return psutil.virtual_memory().used / (1024 ** 3)

    def snapshot(self) -> dict:
        """Return every metric in one dict — handy for the dashboard/logger."""
        return {
            "fps": round(self.fps, 1),
            "processing_ms": round(self.last_processing_ms, 1),
            "cpu_percent": round(self.cpu_usage(), 1),
            "memory_percent": round(self.memory_usage_percent(), 1),
            "memory_gb": round(self.memory_usage_gb(), 2),
        }
