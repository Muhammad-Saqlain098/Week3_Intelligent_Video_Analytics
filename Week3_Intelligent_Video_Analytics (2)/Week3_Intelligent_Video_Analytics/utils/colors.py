"""
colors.py
---------
Consistent BGR color palette used across the whole project so every
module draws in the same visual style.
"""

import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
ORANGE = (0, 150, 255)
PURPLE = (255, 0, 150)

PALETTE = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, PURPLE]


def color_for_id(track_id: int):
    """
    Deterministically map a tracker ID to a color so the same object
    keeps the same color across frames.
    """
    if track_id is None:
        return WHITE
    random.seed(int(track_id) * 999)
    return (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255),
    )
