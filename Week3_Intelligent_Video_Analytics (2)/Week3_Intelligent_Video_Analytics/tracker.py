"""
tracker.py
----------
Wraps YOLO detection + tracking using ultralytics' BUILT-IN tracker
support, which ships with two ready-made configs:

    "bytetrack" -> bytetrack.yaml  (fast, motion-only association)
    "botsort"   -> botsort.yaml    (adds appearance Re-ID + camera-motion
                                    compensation; slower, more robust to
                                    occlusion and camera shake)

This lets Assignment 2 (Tracking Experiments) switch trackers with a
single config value (utils.config.TRACKER_TYPE) instead of installing or
hand-wiring a second tracking library.

The class exposes the same simple interface used throughout the rest of
the project (a `Detections`-like object with .xyxy, .tracker_id,
.class_id, .confidence, and len()), so app.py, counter.py, roi.py, and
trajectory.py don't need to know which tracker is active underneath.

Usage:
    tracker = ObjectTracker(model_path, tracker_type="bytetrack")
    detections = tracker.update(frame)
"""

import numpy as np
from ultralytics import YOLO

from utils import config


class Detections:
    """Minimal, dependency-free stand-in for supervision's Detections object."""

    def __init__(self, xyxy, tracker_id, class_id, confidence):
        self.xyxy = xyxy
        self.tracker_id = tracker_id
        self.class_id = class_id
        self.confidence = confidence

    def __len__(self):
        return len(self.xyxy)

    @staticmethod
    def empty():
        return Detections(
            xyxy=np.zeros((0, 4)),
            tracker_id=np.zeros((0,), dtype=int),
            class_id=np.zeros((0,), dtype=int),
            confidence=np.zeros((0,)),
        )


class ObjectTracker:
    def __init__(self, model_path: str = config.MODEL_PATH, tracker_type: str = None):
        self.model = YOLO(model_path)
        self.class_names = self.model.names
        self.tracker_type = tracker_type or config.TRACKER_TYPE
        self._tracker_yaml = f"{self.tracker_type}.yaml"

    def update(self, frame):
        """
        Run detection + tracking on a single frame using ultralytics'
        built-in `.track()` API with `persist=True` so identities carry
        over between calls (i.e. across video frames).
        Returns a Detections object.
        """
        results = self.model.track(
            frame,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            classes=config.CLASSES_TO_DETECT,
            tracker=self._tracker_yaml,
            persist=True,
            verbose=False,
        )[0]

        boxes = results.boxes
        if boxes is None or boxes.id is None or len(boxes) == 0:
            return Detections.empty()

        xyxy = boxes.xyxy.cpu().numpy()
        tracker_id = boxes.id.cpu().numpy().astype(int)
        class_id = boxes.cls.cpu().numpy().astype(int)
        confidence = boxes.conf.cpu().numpy()

        return Detections(xyxy, tracker_id, class_id, confidence)

    def class_name(self, class_id: int) -> str:
        return self.class_names.get(int(class_id), str(class_id))

    def reset(self):
        """
        Clear internal tracker state. Call this whenever you switch to a
        new video source (webcam restart, new file, etc.) so old track
        IDs from a previous stream don't leak into the new one.
        """
        if hasattr(self.model, "predictor") and self.model.predictor is not None:
            self.model.predictor.trackers = None
