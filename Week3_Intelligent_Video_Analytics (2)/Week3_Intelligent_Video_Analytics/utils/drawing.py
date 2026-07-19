"""
drawing.py
----------
All low-level OpenCV drawing helpers (boxes, labels, lines, panels)
live here so the rest of the codebase stays clean.
"""

import cv2

from utils.colors import color_for_id, WHITE, BLACK


def draw_box(frame, box, tracker_id=None, label=""):
    """Draw a bounding box with an optional ID + label tag above it."""
    x1, y1, x2, y2 = [int(v) for v in box]
    color = color_for_id(tracker_id)

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    text = f"ID {tracker_id} {label}".strip()
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
    cv2.putText(
        frame, text, (x1 + 3, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 2,
    )
    return frame


def draw_center_dot(frame, center, color=(0, 0, 255), radius=4):
    cv2.circle(frame, center, radius, color, -1)
    return frame


def draw_line_counter(frame, start, end, color=(0, 0, 255), thickness=2):
    cv2.line(frame, start, end, color, thickness)
    return frame


def draw_roi(frame, x1, y1, x2, y2, color=(255, 0, 255), name=""):
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
    if name:
        cv2.putText(
            frame, name, (x1, max(y1 - 10, 15)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
        )
    return frame


def draw_trajectory(frame, points, color=(0, 255, 255), thickness=2):
    for i in range(1, len(points)):
        cv2.line(frame, points[i - 1], points[i], color, thickness)
    return frame


def draw_direction_label(frame, position, direction, color=(0, 255, 255)):
    cv2.putText(
        frame, direction, position,
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2,
    )
    return frame


def draw_transparent_panel(frame, top_left, bottom_right, color=(30, 30, 30), alpha=0.55):
    """Draw a semi-transparent filled rectangle (used for the dashboard background)."""
    overlay = frame.copy()
    cv2.rectangle(overlay, top_left, bottom_right, color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame


def put_text_line(frame, text, position, color=WHITE, scale=0.65, thickness=2):
    cv2.putText(
        frame, text, position,
        cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness,
    )
    return frame
