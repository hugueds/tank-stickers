from models import Deviation, PLCInterface, PLCWriteInterface
from classes import Tank, Sticker

def wrong_position(tank, read_plc):
    print('Drain on Wrong Position')
    status = Deviation.DRAIN_POSITION
    error = True

def wrong_quantity():
    print('Found more stickers than needed')
    status = Deviation.STICKER_QUANTITY
    error = True

    print('Sticker not found')
    status = Deviation.STICKER_NOT_FOUND
    error = True

def wrong_label(sticker: Sticker, read_plc: PLCInterface, write_plc :PLCWriteInterface):
    print('Wrong Label, expected:' + str(read_plc.sticker) + ', received: ' + str(sticker.label))
    write_plc.inc_sticker = sticker.label_char_index
    status = Deviation.STICKER_VALUE
    error = True


def wrong_angle():
    print('Wrong Label Angle, expected:' + str(read_plc.sticker_angle) + ', received: ' + str(sticker.angle))
    write_plc.inc_angle = sticker.angle
    status = Deviation.STICKER_ANGLE
    error = True

def wrong_drain():
    print('Wrong Label Position, expected:' + str(self.read_plc.sticker_position) + ', received: ' + str(sticker.quadrant))
    self.write_plc.position_inc_sticker = sticker.quadrant
    status = Deviation.STICKER_POSITION
    error = True
