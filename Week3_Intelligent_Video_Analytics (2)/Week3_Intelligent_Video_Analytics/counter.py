"""
counter.py
----------
Virtual line counter: counts objects crossing a user-defined line and
classifies each crossing as IN or OUT based on direction of travel.
"""

from utils.helpers import get_center


class LineCounter:
    def __init__(self, start, end):
        """
        start, end : (x, y) tuples defining the counting line.
        Uses the classic "which side of the line" sign-test so it works
        for lines of any orientation (horizontal, vertical, diagonal).
        """
        self.start = start
        self.end = end

        self.in_count = 0
        self.out_count = 0

        # Remember which side of the line each tracker_id was last seen on
        self._last_side = {}

    def _side_of_line(self, point):
        """
        Returns positive, negative, or zero depending on which side of the
        line the point lies on (2D cross product test).
        """
        (x1, y1), (x2, y2) = self.start, self.end
        px, py = point
        return (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)

    def update(self, tracker_id, box):
        """
        Call once per tracked object per frame. Detects a line crossing
        and updates in_count / out_count accordingly.
        Returns "IN", "OUT", or None if no crossing happened this frame.
        """
        x1, y1, x2, y2 = box
        center = get_center(x1, y1, x2, y2)
        side = self._side_of_line(center)

        event = None
        if tracker_id in self._last_side:
            prev_side = self._last_side[tracker_id]
            if prev_side <= 0 < side:
                self.in_count += 1
                event = "IN"
            elif prev_side >= 0 > side:
                self.out_count += 1
                event = "OUT"

        self._last_side[tracker_id] = side
        return event

    @property
    def counts(self):
        return {"in": self.in_count, "out": self.out_count}
