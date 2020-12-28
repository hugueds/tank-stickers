import cv2 as cv
import numpy as np
from datetime import datetime
from time import sleep
from threading import Thread
from models import AppState, PLCInterface, PLCWriteInterface
from classes import Tank, Sticker, PLC, Camera
from classes.commands import *
from classes.image_writter import *
from classes.tf_model import TFModel
from logger import logger

class Controller:

    camera_side = 0 # 0 = Middle, 1 = Right, 2 = Left
    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    read_plc: PLCInterface
    write_plc: PLCWriteInterface
    start_time = datetime.now()
    tank: Tank
    camera_enabled = True
    start_time: datetime
    frame: np.ndarray

    def __init__(self):
        # self.plc = PLC()
        self.start_time = datetime.now()
        self.tank = Tank()
        self.camera = Camera()
        self.camera.start()
        self.model = TFModel()

    def get_frame(self):
        success, self.frame = self.camera.read()

    def show_circle(self):
        self.tank.find_circle()
        frame = self.frame.copy()
        frame = draw_tank_circle(frame, self.tank)

    def show(self):
        frame = self.frame.copy()
        if self.tank.found:
            frame = draw_tank_center_axis(frame, self.tank)
            frame = draw_tank_rectangle(frame, self.tank)
            frame = draw_sticker(frame, self.camera, self.tank)

        frame = draw_camera_info(frame, self.camera)
        # frame = draw_plc_status(frame, self.camera, self.plc)
        frame = draw_roi_lines(frame, self.camera)
        frame = draw_center_axis(frame, self.camera)
        self.camera.show(frame)

    def process(self, frame: np.ndarray = 0):
        if not frame:
            frame = self.frame
        self.tank.find(frame)
        if self.tank.found:
            # if it is a superior tank, find the drain -- addicional, compare the drain position
            self.tank.get_sticker_position_lab(frame) # count how many times sticker is the same before proceed (e.g 10x)
            for sticker in self.tank.stickers:
                # check if it is only one sticker, if it is required and if it is on right quadrant based on the drain if it is superior
                sticker.label_index, sticker.label = self.model.predict(sticker.image)
                sticker.update_position()

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
            self.read_plc = self.plc.read_v2()
            self.write_plc.update_life_beat()
            data = self.write_plc.get_bytearray()
            self.plc.write_v2(data)
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
            logger.info(f'Saving results to {path}')
            # log to a different result path
            cv.imwrite(path, self.frame)
        except Exception as e:
            logger.exception(e)


    def update_camera_setting(self):
        pass








