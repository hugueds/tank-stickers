import cv2 as cv
import numpy as np
from datetime import datetime
from time import sleep
from threading import Thread
from pathlib import Path
from collections import Counter
from classes.camera import Camera
from classes.plc import PLC
from classes.tank import Tank
from classes.sticker import Sticker
from classes.commands import key_pressed
from classes.image_writter import *
from classes.tf_model import TFModel
from models import AppState, PLCInterface, PLCWriteInterface
from logger import logger, results_logger

class Controller:

    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    read_plc: PLCInterface = PLCInterface()
    write_plc: PLCWriteInterface = PLCWriteInterface(0)
    start_time = datetime.now()
    tank: Tank = Tank()
    camera_enabled = True
    start_time: datetime
    frame: np.ndarray = np.zeros((640,480))
    file_frame = None
    result_list = []
    final_result = False
    drain_model: TFModel = None

    def __init__(self, is_picture=False):
        self.start_time = datetime.now()
        self.tank = Tank()
        self.camera = Camera()
        self.plc = PLC(self.camera.number)
        self.is_picture = is_picture
        if not is_picture:
            self.camera.start()
        self.model = TFModel(model_name='sticker')

    def get_frame(self):
        if self.is_picture:
            self.frame = self.file_frame
            return
        success, self.frame = self.camera.read()

    def open_file(self, file):
        self.frame = cv.imread(file)
        self.file_frame = self.frame

    def process(self):
        if self.camera.number == 1:
            self.__process_up_camera()
        else:
            self.__process_side_camera()

    def __process_up_camera(self):
        # self.tank.find(self.frame)
        self.tank.find_2(self.frame) # TODO: unify strategies
        if self.tank.found:
            if self.drain_model == None:
                self.drain_model = TFModel(model_name='drain') # to be implemented
            self.tank.get_drain_ml(self.frame, self.drain_model)
            self.tank.get_sticker_position_lab(self.frame)
            self.__predict_sticker()

    def __process_side_camera(self):
        # self.tank.find_in_circle(self.frame)
        self.tank.find_convex(self.frame)
        if self.tank.found:
            self.tank.get_sticker_position(self.frame)
            self.__predict_sticker()

    def __predict_sticker(self):
        for sticker in self.tank.stickers:
                sticker.label_index, sticker.label = self.model.predict(sticker.image)
                sticker.update_label_info()

    def analyse(self) -> None:
        self.__clear_plc()
        error = False
        sticker = Sticker()
        status = 0
        if not self.tank.found:
            self.write_plc.cam_status = 0
            return
        if self.tank.check_drain and self.read_plc.drain_camera and (self.read_plc.drain_position != self.tank.drain_position):
            print('Drain on Wrong Position')
            self.write_plc.cam_status = 7
            error = True
        if len(self.tank.stickers) > 1:
            print('Found more stickers than needed')
            self.write_plc.cam_status = 2
            error = True
        if self.read_plc.sticker_camera and len(self.tank.stickers) == 0:
            print('Sticker not found')
            self.write_plc.cam_status = 3
            error = True
        if len(self.tank.stickers):
            sticker = self.tank.stickers[0]
        if self.read_plc.sticker_camera and self.read_plc.sticker != sticker.label_char_index:
            print('Wrong Label, expected:' + str(self.read_plc.sticker) + ', received: ' + str(sticker.label))
            self.write_plc.inc_sticker = sticker.label_char_index
            self.write_plc.cam_status = 9
            error = True
        if self.read_plc.sticker_camera and self.read_plc.sticker_angle != sticker.angle:
            print('Wrong Label Angle, expected:' + str(self.read_plc.sticker_angle) + ', received: ' + str(sticker.angle))
            self.write_plc.inc_angle = sticker.angle
            self.write_plc.cam_status = 8
            error = True
        if self.read_plc.sticker_camera and self.read_plc.sticker_position != sticker.quadrant:
            print('Wrong Label Position, expected:' + str(self.read_plc.sticker_position) + ', received: ' + str(sticker.quadrant))
            self.write_plc.position_inc_sticker = sticker.quadrant
            self.write_plc.cam_status = 2
            error = True

        if not error:
            self.__job_done()

        # TO IMPLEMENT
        # Check the highest arg in last 5 frames
        if not error:
            self.write_plc.cam_status = 1

        self.result_list.append(self.write_plc.cam_status)

        if len(self.result_list > 5):
            self.result_list.pop(0)
        if Counter(self.result_list).most_common()[0][0] == 1:
            self.__job_done()

        # ----------------------------------------------------





    def __job_done(self):
        self.final_result = True
        self.write_plc.cam_status = 1
        self.write_plc.job_status = 2
        self.write_plc.request_ack = False

    def show(self) -> None:
        frame = self.frame.copy()
        if self.tank.found:
            frame = draw_tank_center_axis(frame, self.tank)
            frame = draw_tank_rectangle(frame, self.tank)
            frame = draw_sticker(frame, self.camera, self.tank)
            frame = draw_drain_ml(frame, self.tank)
        frame = draw_roi_lines(frame, self.camera)
        frame = draw_center_axis(frame, self.camera)
        frame = draw_camera_info(frame, self.camera)
        frame = draw_plc_status(frame, self.plc, self.read_plc, self.write_plc)
        self.camera.show(frame)

    def get_fake_parameters(self) -> None:
        self.read_plc.read_request = True
        self.read_plc.sticker = 1
        self.read_plc.sticker_angle = 2
        self.read_plc.sticker_position = 4
        self.read_plc.drain_position = 0

    def confirm_request(self) -> None:
        self.read_plc.read_request = False
        self.write_plc.request_ack = True
        self.write_plc.cam_status = 0
        self.write_plc.job_status = 1
        self.final_result = False
        self.result_list.clear()
        self.__clear_plc()

    def __clear_plc(self) -> None:
        self.write_plc.position_inc_drain = 0
        self.write_plc.position_inc_sticker = 0
        self.write_plc.inc_sticker = 0
        self.write_plc.inc_angle = 0

    def get_command(self) -> None:
        key = cv.waitKey(1) & 0xFF
        key_pressed(key, self.camera, self.tank)
        if key == ord('n'):
            self.get_fake_parameters()
        elif key == ord('o'):
            self.__job_done()
        elif key == ord('i'):
            self.__print_plc_values()
        if self.read_plc.read_command:
            # send_command() # TODO Define and receive commands from PLC
            pass

    def __print_plc_values(self) -> None:
        print('PLC READ:')
        print(self.read_plc.__dict__)
        print('PLC WRITE:')
        print(self.write_plc.__dict__)

    def send_command(self, key) -> None:
        key_pressed(key, self.camera, self.tank)

    def start_plc(self) -> None:
        logger.info('Starting PLC Thread')
        self.plc.connect()
        self.write_plc = PLCWriteInterface(self.plc.db_write['size'])
        Thread(name='thread_plc', target=self.update_plc, daemon=True).start()

    def update_plc(self) -> None:
        last_life_beat = -1
        while self.plc.enabled:
            read_data = self.plc.read()
            self.read_plc.update(read_data)
            if self.read_plc.life_beat == last_life_beat:
                logger.error('PLC is not responding... Trying to reconnect')
                self.plc.disconnect()
                sleep(5)
                self.plc.connect()
            else:
                last_life_beat = self.read_plc.life_beat
                self.write_plc.update_life_beat()
                self.plc.write(self.write_plc)
                sleep(self.plc.update_time)
        else:
            logger.warning('PLC is not Enabled')

    def set_state(self, state: AppState) -> None:
            logger.info(f'Updating state to: {state}')
            self.state = state

    def save_result(self) -> None:
        try:
            now = datetime.now()
            path = f'../results/{now.year}/{now.month}/{now.day}/{self.read_plc.popid}'
            Path(path).mkdir(parents=True, exist_ok=True)
            file = f'{path}/{now.strftime("%H%M%S")}_{self.read_plc.partnumber}.jpg'
            logger.info(f'Saving results to {path}')
            cv.imwrite(file, self.frame)
            results_logger.info(f'{self.read_plc.popid} - {self.read_plc.partnumber} - {self.read_plc.parameter}')
        except Exception as e:
            logger.exception(e)









