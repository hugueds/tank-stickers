import numpy as np

class Sticker:

    label = ''
    label_index = 0
    label_char = ''
    label_char_index = 255
    position = 255
    angle = 255
    area = 0
    quadrant = 0
    found = False
    debug = False
    image: np.ndarray = 0