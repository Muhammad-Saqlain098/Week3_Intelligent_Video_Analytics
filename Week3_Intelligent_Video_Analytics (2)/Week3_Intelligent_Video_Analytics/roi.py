"""
roi.py
------
Region of Interest (ROI) monitoring. Supports multiple named zones and
reports how many tracked objects currently fall inside each one.
"""

from utils.helpers import get_center
from utils.drawing import draw_roi


class ROIZone:
    def __init__(self, name, x1, y1, x2, y2, color=(255, 0, 255)):
        self.name = name
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.color = color
        self.current_ids = set()

    def contains(self, center):
        cx, cy = center
        return self.x1 < cx < self.x2 and self.y1 < cy < self.y2

    def draw(self, frame):
        return draw_roi(frame, self.x1, self.y1, self.x2, self.y2, self.color, self.name)


class ROIManager:
    def __init__(self, zones_config):
        self.zones = [
            ROIZone(z["name"], z["x1"], z["y1"], z["x2"], z["y2"], z.get("color", (255, 0, 255)))
            for z in zones_config
        ]

    def update(self, tracker_id, box):
        """Check a single tracked box against every zone."""
        x1, y1, x2, y2 = box
        center = get_center(x1, y1, x2, y2)
        inside_zones = []
        for zone in self.zones:
            if zone.contains(center):
                zone.current_ids.add(tracker_id)
                inside_zones.append(zone.name)
            else:
                zone.current_ids.discard(tracker_id)
        return inside_zones

    def reset_frame(self):
        """Call once per frame before updating, so stale IDs are cleared."""
        for zone in self.zones:
            zone.current_ids = set()

    def draw_all(self, frame):
        for zone in self.zones:
            zone.draw(frame)
        return frame

    def counts(self):
        return {zone.name: len(zone.current_ids) for zone in self.zones}

    def total_count(self):
        return sum(len(zone.current_ids) for zone in self.zones)
