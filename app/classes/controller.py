import cv2 as cv
import numpy as np
from datetime import datetime
from time import sleep
from threading import Thread
from models import AppState, PLCInterface, PLCWriteInterface
from classes import Tank, PLC, Camera
from classes.commands import *
from classes.image_writter import *
from classes.tf_model import TFModel
from logger import logger

class Controller:

    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    read_plc: PLCInterface = PLCInterface()
    write_plc: PLCWriteInterface
    start_time = datetime.now()
    tank: Tank = Tank()
    camera_enabled = True
    start_time: datetime
    frame: np.ndarray = None
    img_frame = None
    is_picture = True
    result = False

    def __init__(self, is_picture=False):
        self.start_time = datetime.now()
        self.tank = Tank()
        self.camera = Camera()
        self.camera.start()
        self.is_picture = is_picture
        self.plc = PLC()
        self.write_plc = PLCWriteInterface(self.plc.db['size'])
        self.model = TFModel()

    def get_frame(self):
        if not self.is_picture:
            success, self.frame = self.camera.read()
        else:
            self.frame = self.img_frame

    def read_file(self, file):
        if self.frame is None:
            self.frame = cv.imread(file)
            self.img_frame = self.frame

    def show_circle(self):
        frame = self.frame.copy()
        self.tank.find_circle(frame)
        frame = draw_tank_circle(frame, self.tank)
        self.camera.show(frame)

    def show(self):
        frame = self.frame.copy()
        if self.tank.found:
            frame = draw_tank_center_axis(frame, self.tank)
            frame = draw_tank_rectangle(frame, self.tank)
            frame = draw_sticker(frame, self.camera, self.tank)

        frame = draw_camera_info(frame, self.camera)
        frame = draw_plc_status(frame, self.plc, self.read_plc, self.write_plc)
        frame = draw_roi_lines(frame, self.camera)
        frame = draw_center_axis(frame, self.camera)
        self.camera.show(frame)
        self.camera.update_frame_counter()

    def process(self, frame: np.ndarray = 0):
        if not frame:
            frame = self.frame
        if self.camera.number != 1:
            self.tank.find_circle(frame)
            if self.tank.found:
                self.tank.get_sticker_position_lab(frame)
                for sticker in self.tank.stickers:
                    # check if it is only one sticker, if it is required and if it is on right quadrant based on the drain if it is superior
                    sticker.label_index, sticker.label = self.model.predict(sticker.image)
                    sticker.update_position()
        else:
            self.tank.find(frame)
            if self.tank.found:
                self.tank.get_drain_lab(frame)
                self.tank.get_sticker_position_lab(frame) # count how many times sticker is the same before proceed (e.g 10x)
                # self.tank.get_sticker_position(frame) # count how many times sticker is the same before proceed (e.g 10x)
                for sticker in self.tank.stickers:
                    # check if it is only one sticker, if it is required and if it is on right quadrant based on the drain if it is superior
                    sticker.label_index, sticker.label = self.model.predict(sticker.image)
                    sticker.update_position()

    def analyse(self):
        # compare if requested PLC info matches processed image
        if self.read_plc.drain_camera and self.read_plc.drain_position != self.tank.drain_position:
            logger.error('Drain on Wrong Position')
            return
        if len(self.tank.stickers) > 1:
            logger.error('There are more stickers than needed')
            return
        if len(self.tank.stickers) == 0 and self.read_plc.sticker_camera:
            logger.error('Sticker not found')
            return
        sticker = self.tank.stickers[0]
        if self.read_plc.sticker != sticker.label:
            logger.error('Wrong Label, expected: {}, received: {}')
            self.write_plc.inc_sticker = sticker.label
        if self.read_plc.sticker_angle != sticker.angle:
            logger.error('Wrong Label Angle, expected: {}, received: {}')
            self.write_plc.inc_angle = sticker.angle
        if self.read_plc.sticker_position != sticker.quadrant:
            logger.error('Wrong Label Angle, expected: {}, received: {}')
            self.write_plc.position_inc_sticker = sticker.quadrant

        self.result = True
        self.write_plc.cam_status = 1


    def confirm_request(self):
        self.result = False
        self.write_plc.request_ack = True
        self.write_plc.job_status = 1
        self.write_plc.cam_status = 0
        self.write_plc.position_inc_drain = 0
        self.write_plc.position_inc_sticker = 0
        self.write_plc.inc_sticker = 0
        self.write_plc.inc_angle = 0

    def get_command(self):
        key = cv.waitKey(1) & 0xFF
        key_pressed(key, self.camera, self.tank)

    def start_plc(self):
        logger.info('Starting PLC Thread')
        self.plc.connect()
        self.write_plc = PLCWriteInterface(self.plc.db['size'])
        Thread(name='thread_plc', target=self.update_plc, daemon=True).start()

    def set_state(self, state: AppState):
        logger.info(f'Updating state to: {state}')
        self.state = state

    def update_plc(self):
        last_life_beat = -1
        while self.plc.enabled:
            read_data = self.plc.read()
            self.read_plc = PLCInterface(read_data)
            self.write_plc.update_life_beat()
            data = self.write_plc.get_bytearray()
            self.plc.write(data)
            if self.read_plc.life_beat == last_life_beat:
                logger.error('PLC is not responding... Trying to reconnect')
                self.plc.disconnect()
                sleep(1)
                self.plc.connect()
            else:
                last_life_beat = self.read_plc.life_beat
            sleep(self.plc.update_time)
        else:
            logger.warning('PLC is not Enabled')

    def save_result(self):
        try:
            now = datetime.now()
            file = f'{now.strftime("%Y%m%d-%H%M%S")}_{self.read_plc.parameter}.jpg'
            path = f'../results/{now.year}/{now.month}/{now.day}/{self.read_plc.popid}/{file}'
            logger.info('Saving results to {path}')
            # log to a different result path
            cv.imwrite(path, self.frame)
        except Exception as e:
            logger.exception(e)









