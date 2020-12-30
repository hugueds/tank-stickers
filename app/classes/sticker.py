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

    def __init__(self, x=0, y=0, w=0, h=0, area=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.area = area

    def set_relative(self, tank):
        zero_x, zero_y = int(tank.w // 2), int(tank.h // 2)
        self.relative_x = (self.x - zero_x) - tank.x + (self.w // 2)
        self.relative_y = tank.y - (self.y - zero_y) - (self.h // 2)

    def update_position(self):
        if self.label_index <= 3:
            self.position = 0
        elif self.label_index >= 4 and self.label_index < 7:
            self.position = 180
        else:
            self.position = 90

    def calc_quadrant(self, tank_x, tank_y, tank_w, tank_h):
        row, col = -1, -1

        q_list = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]

        temp_x = (self.x - tank_x) / tank_w
        temp_y = (self.y - tank_y) / tank_h

        if temp_x <= 0.3:
            col = 0
        elif temp_x > 0.3 and temp_x < 0.6:
            col = 1
        else:
            col = 2

        if temp_y <= 0.3:
            row = 0
        elif temp_y > 0.3 and temp_y < 0.6:
            row = 1
        else:
            row = 2

        self.quadrant = q_list[row][col]
