"""
logger.py
---------
Writes every detection to a CSV file for later reporting / auditing.
"""

import csv
import os
import time

from utils.helpers import ensure_dir


class DetectionLogger:
    def __init__(self, log_path: str):
        self.log_path = log_path
        ensure_dir(log_path)

        self._file = open(log_path, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(
            ["Timestamp", "Frame", "Tracker_ID", "Class", "Confidence",
             "X1", "Y1", "X2", "Y2", "ROI_Zones", "Direction"]
        )

    def log(self, frame_count, tracker_id, class_name, confidence, box, roi_zones=None, direction=""):
        x1, y1, x2, y2 = [round(float(v), 1) for v in box]
        self._writer.writerow(
            [
                round(time.time(), 3),
                frame_count,
                tracker_id,
                class_name,
                round(float(confidence), 3),
                x1, y1, x2, y2,
                "|".join(roi_zones) if roi_zones else "",
                direction,
            ]
        )

    def flush(self):
        self._file.flush()

    def close(self):
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
