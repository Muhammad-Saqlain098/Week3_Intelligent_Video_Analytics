"""
dashboard.py
------------
Draws the semi-transparent "Analytics Dashboard" panel onto each frame,
summarizing every live statistic the system produces.
"""

from utils.drawing import draw_transparent_panel, put_text_line
from utils.colors import WHITE, YELLOW, CYAN, ORANGE, GREEN, RED
from utils import config


class Dashboard:
    def __init__(self, top_left=(10, 10), width=340):
        self.top_left = top_left
        self.width = width

    def render(self, frame, stats: dict):
        """
        stats keys expected (all optional, missing ones are skipped):
            fps, current_objects, total_in, total_out, roi_counts (dict),
            avg_confidence, processing_ms, cpu_percent, memory_percent
        """
        x, y = self.top_left
        line_h = 28
        lines = []

        lines.append(("Intelligent Video Analytics", WHITE, 0.7))
        if "fps" in stats:
            lines.append((f"FPS            : {stats['fps']:.1f}", GREEN, 0.6))
        if "current_objects" in stats:
            lines.append((f"Current Objects: {stats['current_objects']}", WHITE, 0.6))
        if "total_in" in stats and "total_out" in stats:
            lines.append((f"IN / OUT       : {stats['total_in']} / {stats['total_out']}", CYAN, 0.6))
        if "roi_counts" in stats and stats["roi_counts"]:
            total_roi = sum(stats["roi_counts"].values())
            lines.append((f"ROI Objects    : {total_roi}", (255, 0, 255), 0.6))
        if "avg_confidence" in stats:
            lines.append((f"Avg Confidence : {stats['avg_confidence']*100:.1f}%", YELLOW, 0.6))
        if "processing_ms" in stats:
            lines.append((f"Inference Time : {stats['processing_ms']:.1f} ms", CYAN, 0.6))
        if "cpu_percent" in stats:
            lines.append((f"CPU Usage      : {stats['cpu_percent']:.1f}%", ORANGE, 0.6))
        if "memory_percent" in stats:
            lines.append((f"Memory Usage   : {stats['memory_percent']:.1f}%", (255, 150, 255), 0.6))

        panel_height = line_h * len(lines) + 20
        draw_transparent_panel(
            frame,
            (x, y),
            (x + self.width, y + panel_height),
            color=config.DASHBOARD_BG_COLOR,
            alpha=config.DASHBOARD_ALPHA,
        )

        for i, (text, color, scale) in enumerate(lines):
            put_text_line(frame, text, (x + 15, y + 30 + i * line_h), color=color, scale=scale)

        return frame
