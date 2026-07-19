"""
tracker_supervision.py
-----------------------
REFERENCE IMPLEMENTATION — kept for Assignment 2 (Tracking Experiments)
comparison purposes.

This is the original ByteTrack integration built directly on the
`supervision` library's ByteTrack class, separate from ultralytics'
built-in tracker YAMLs used by the main `tracker.py`. It is useful for
comparing "manual" ByteTrack parameter tuning against ultralytics'
built-in bytetrack.yaml / botsort.yaml configs.

Wraps YOLO detection + ByteTrack (via the `supervision` library) behind
one simple class: ObjectTracker.

Usage:
    tracker = ObjectTrackerSupervision(model_path)
    detections = tracker.update(frame)
"""

from ultralytics import YOLO
import supervision as sv

from utils import config


class ObjectTrackerSupervision:
    def __init__(self, model_path: str = config.MODEL_PATH):
        self.model = YOLO(model_path)
        self.class_names = self.model.names

        self.byte_tracker = sv.ByteTrack(
            track_activation_threshold=config.TRACK_ACTIVATION_THRESHOLD,
            lost_track_buffer=config.LOST_TRACK_BUFFER,
            minimum_matching_threshold=config.MINIMUM_MATCHING_THRESHOLD,
            frame_rate=config.FRAME_RATE,
        )

    def detect(self, frame):
        """Run YOLO inference on a single frame and return sv.Detections."""
        results = self.model(
            frame,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            classes=config.CLASSES_TO_DETECT,
            verbose=False,
        )[0]

        detections = sv.Detections.from_ultralytics(results)
        return detections

    def update(self, frame):
        """Detect + track. Returns an sv.Detections object with tracker_id set."""
        detections = self.detect(frame)
        detections = self.byte_tracker.update_with_detections(detections)
        return detections

    def class_name(self, class_id: int) -> str:
        return self.class_names.get(int(class_id), str(class_id))
