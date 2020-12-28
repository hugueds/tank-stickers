import numpy as np

class Sticker:

    label = ""
    label_index = 0
    position = 255
    angle = 999
    area = 0
    quadrant = 0
    found = False
    debug = False
    image: np.ndarray = 0

    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def update_position(self):
        if self.label_index <= 3:
            self.position = 0
        elif self.label_index >= 4 and self.label_index < 7:
            self.position = 180
        else:
            self.position = 90


    def calc_quadrant(self, tank):
        temp_x = 0
        temp_y = 0
        res = 0
        quad_list = [5, 10, 15, 7, 14, 21, 11, 22, 33]

        if self.x < tank.w * 0.33:
            temp_x = 1
        elif self.x < tank.w * 0.66 and self.x > 0.33:
            temp_x = 2
        elif self.x >= tank.w * 0.66:
            temp_x = 3

        if self.y < tank.h * 0.33:
            temp_y = 5
        elif self.y < tank.h * 0.66 and self.y > 0.33:
            temp_y = 7
        elif self.y >= tank.h * 0.66:
            temp_y = 11

        res = temp_x * temp_y

        self.quadrant = quad_list.index(res) + 1
