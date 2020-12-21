from snap7.util import *

class PLCInterface:

    life_beat = 0
    life_bit = True

    def __init__(self, data):
        self.life_beat = get_bool(data, 0, 0) 
        pass
