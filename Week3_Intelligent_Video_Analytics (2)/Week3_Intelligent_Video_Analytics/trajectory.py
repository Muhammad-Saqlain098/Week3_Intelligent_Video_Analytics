"""
trajectory.py
-------------
Tracks per-object movement history, draws trajectories, and computes
a simple direction label (UP / DOWN / LEFT / RIGHT / diagonal combos).
"""

from collections import deque

from utils.helpers import get_center
from utils.drawing import draw_trajectory, draw_direction_label
from utils import config


class TrajectoryTracker:
    def __init__(self, max_length=config.TRAJECTORY_MAX_LENGTH):
        self.max_length = max_length
        self.history = {}   # tracker_id -> deque of (x, y) points

    def update(self, tracker_id, box):
        """Append the current center point to this object's history."""
        x1, y1, x2, y2 = box
        center = get_center(x1, y1, x2, y2)

        if tracker_id not in self.history:
            self.history[tracker_id] = deque(maxlen=self.max_length)

        self.history[tracker_id].append(center)
        return center

    def get_direction(self, tracker_id):
        """Return a human-readable direction string, or '' if not enough data."""
        points = self.history.get(tracker_id)
        if not points or len(points) < 2:
            return ""

        old_x, old_y = points[-2]
        new_x, new_y = points[-1]

        vertical = ""
        horizontal = ""

        if new_y - old_y > 2:
            vertical = "DOWN"
        elif old_y - new_y > 2:
            vertical = "UP"

        if new_x - old_x > 2:
            horizontal = "RIGHT"
        elif old_x - new_x > 2:
            horizontal = "LEFT"

        if vertical and horizontal:
            return f"{vertical}-{horizontal}"
        return vertical or horizontal or "STATIC"

    def draw(self, frame, tracker_id, color=config.TRAJECTORY_COLOR):
        points = list(self.history.get(tracker_id, []))
        if len(points) >= 2:
            draw_trajectory(frame, points, color=color, thickness=config.TRAJECTORY_THICKNESS)
        return frame

    def draw_all(self, frame):
        for tracker_id in self.history:
            self.draw(frame, tracker_id)
        return frame

    def annotate_direction(self, frame, tracker_id, box):
        x1, y1, x2, y2 = box
        cx, cy = get_center(x1, y1, x2, y2)
        direction = self.get_direction(tracker_id)
        if direction:
            draw_direction_label(frame, (cx, int(y1) - 20), direction)
        return direction

    def cleanup(self, active_ids):
        """Drop history for IDs no longer being tracked (keeps memory bounded)."""
        stale = [tid for tid in self.history if tid not in active_ids]
        for tid in stale:
            del self.history[tid]
