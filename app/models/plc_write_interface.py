from snap7.util import set_bool

class PLCWriteInterface:

    _bytearray: bytearray

    def __init__(self, size):
        self.request_ack = False
        self.drain_found = False
        self.tank_found = False
        self.life_beat = 0
        self.job_status = 0
        self.cam_status = 0
        self.inc_sticker = 0
        self.position_inc_sticker = 0
        self.position_inc_drain = 0
        self.inc_angle = 0
        self.size = size

    def get_bytearray(self) -> bytearray:

        _bytearray = bytearray(self.size)

        set_bool(_bytearray,0, 0, self.request_ack)
        set_bool(_bytearray,0, 1, self.drain_found)
        set_bool(_bytearray,0, 2, self.tank_found)
        _bytearray[1] = self.life_beat
        _bytearray[2] = self.job_status
        _bytearray[3] = self.cam_status
        _bytearray[4] = self.inc_sticker
        _bytearray[5] = self.position_inc_drain
        _bytearray[6] = self.position_inc_sticker
        _bytearray[7] = self.inc_angle
        _bytearray[8] = self.inc_sticker

        self._bytearray = _bytearray
        return _bytearray

    def update_life_beat(self) -> None:
        if self.life_beat < 255:
            self.life_beat += 1
        else:
            self.life_beat = 0
