from snap7.util import *

class PLCInterface:

    read_request = False

    def __init__(self, data=None):
        if data is None:
            return
        self.read_request = get_bool(data, 0, 0)
        self.sticker_camera = get_bool(data, 0, 1)
        self.drain_camera = get_bool(data, 0, 2)
        self.life_beat = int(data[2])
        self.sticker = int(data[3])
        self.drain_position = int(data[4])
        self.sticker_position = int(data[5])
        self.sticker_angle = int(data[6])
        self.command = int(data[7])
        self.popid = get_string(data, 8, 8)
        self.parameter = get_string(data, 18, 10)
        self.tank = get_string(data, 30, 8)

