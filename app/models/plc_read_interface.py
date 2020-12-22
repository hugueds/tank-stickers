from snap7.util import *

class PLCInterface:

    life_beat = 0
    life_bit = True
    command = None
    request = False
    quadrant = 0
    sticker = ''
    angle = 255    


    def __init__(self, data):
        self.life_beat = get_bool(data, 0, 0) 
        pass
