"""
heatmap.py
----------
Bonus feature: builds a fading heatmap of where objects spend the most
time, and overlays it on the frame.
"""

import numpy as np
import cv2

from utils.helpers import get_center


class HeatmapGenerator:
    def __init__(self, frame_shape, radius=15, decay=0.98, colormap=cv2.COLORMAP_JET):
        h, w = frame_shape[:2]
        self.heat = np.zeros((h, w), dtype=np.float32)
        self.radius = radius
        self.decay = decay
        self.colormap = colormap

    def update(self, boxes):
        """boxes: iterable of (x1, y1, x2, y2) for the current frame."""
        self.heat *= self.decay
        for box in boxes:
            x1, y1, x2, y2 = box
            cx, cy = get_center(x1, y1, x2, y2)
            cv2.circle(self.heat, (cx, cy), self.radius, 1.0, -1)

    def overlay(self, frame, alpha=0.4):
        normalized = np.clip(self.heat / (self.heat.max() + 1e-6) * 255, 0, 255).astype(np.uint8)
        colored = cv2.applyColorMap(normalized, self.colormap)
        blended = cv2.addWeighted(colored, alpha, frame, 1 - alpha, 0)
        return blended
