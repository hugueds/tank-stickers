from models import Deviation, PLCInterface, PLCWriteInterface
from classes import Tank, Sticker

def wrong_position(tank, read_plc):
    print('Drain on Wrong Position')
    return Deviation.DRAIN_POSITION

def wrong_quantity():
    print('Found more stickers than needed')
    return Deviation.STICKER_QUANTITY

def sticker_not_found():
    print('Sticker not found')
    return Deviation.STICKER_NOT_FOUND

def wrong_label(expected, received):
    print('Wrong Label, expected:' + str(expected) + ', received: ' + str(received))
    return Deviation.STICKER_VALUE

def wrong_angle(expected_angle, angle):
    print('Wrong Label Angle, expected:' + str(expected_angle) + ', received: ' + str(angle))
    return Deviation.STICKER_ANGLE

def wrong_drain(expected_position, quadrant):
    print('Wrong Label Position, expected:' + str(expected_position) + ', received: ' + str(quadrant))
    return Deviation.STICKER_POSITION
