from typing import List


class Tank:

    found = False
    image: np.ndarray = 0
    x, y, w, h = 0, 0, 0, 0
    circle: List[int] = []
    sticker_count = 0
    stickers: List[Sticker] = []
    quantity = 0
    sticker_quadrant = 0
    drain: Drain
    drain_found = False
    drain_position: int = 0
    drain_x, drain_y, drain_w, drain_h = 0, 0, 0, 0
    drain_rel_x, drain_rel_y = 0, 0
    debug_tank = False
    debug_sticker = False
    debug_drain = False