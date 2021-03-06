import numpy as np
from models.quadrants import get_quadrant

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

    def __init__(self, x=0, y=0, w=0, h=0, area=0) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.area = area

    def set_relative(self, tank) -> None:
        zero_x, zero_y = int(tank.w // 2), int(tank.h // 2)
        self.relative_x = (self.x - zero_x) - tank.x + (self.w // 2)
        self.relative_y = tank.y - (self.y - zero_y) - (self.h // 2)

    def update_label_info(self) -> None:
        self.label_char = (self.label.split('_')[0]).lower()
        sticker_chars = ['1', '2', 'p', 't']
        self.label_char_index = sticker_chars.index(self.label_char) + 1
        self.update_label_angle()
        if self.label_index <= 3:
            self.position = 0
        elif self.label_index >= 4 and self.label_index < 7:
            self.position = 1
        else:
            self.position = 2

    def update_label_angle(self) -> None:
        split = self.label.split('_')
        if len(split) == 1:
            self.angle = 1
        else:
            if split[1] == '90':
                self.angle = 2
            else:
                self.angle = 3

    def calc_quadrant(self, tank_x:int, tank_y:int, tank_w:int, tank_h:int, camera: int) -> None:
        row, col = -1, -1

        q_list = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]

        col_tolerance = [0.3, 0.6]
        row_tolerance = [0.3, 0.6]

        temp_x = (self.x - tank_x) / tank_w
        temp_y = (self.y - tank_y) / tank_h

        if temp_x <= col_tolerance[0]:
            col = 0
        elif temp_x > col_tolerance[0] and temp_x < col_tolerance[1]:
            col = 1
        else:
            col = 2

        if temp_y <= row_tolerance[0]:
            row = 0
        elif temp_y > row_tolerance[0] and temp_y < row_tolerance[1]:
            row = 1
        else:
            row = 2

        quad = q_list[row][col]

        self.quadrant = get_quadrant(camera, quad)


