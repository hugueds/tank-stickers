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
from models import AppState, PLCInterface, PLCWriteInterface, Deviation, JobStatus, job_status
from logger import logger, results_logger

class Controller:

    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    read_plc: PLCInterface = PLCInterface()
    write_plc: PLCWriteInterface = PLCWriteInterface(0)
    tank: Tank = Tank()
    frame: np.ndarray = np.zeros((640,480))
    drain_model: TFModel = None
    file_frame = None
    result_list = []
    final_result = False
    analyse_counter = 0
    last_request = 0
    total_reads = 3

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
        else:
            _, self.frame = self.camera.read()

    def open_file(self, file):
        self.frame = cv.imread(file)
        self.file_frame = self.frame

    def process(self):
        self.tank.find(self.camera.number, self.frame, self.read_plc.partnumber)
        self.write_plc.tank_found = self.tank.found
        if self.tank.found:
            self.tank.get_sticker_position(self.frame)
            self.__predict_sticker()
            if self.read_plc.drain_camera:
                if self.drain_model == None:
                    self.drain_model = TFModel(model_name='drain')
                self.tank.get_drain_ml(self.frame, self.drain_model)

    def __predict_sticker(self):
        for sticker in self.tank.stickers:
            sticker.label_index, sticker.label = self.model.predict(sticker.image)
            sticker.update_label_info()

    def analyse(self) -> None:
        self.__clear_plc()
        sticker = Sticker()
        status: Deviation = Deviation.NONE
        qnt_stickers = len(self.tank.stickers)

        if not self.tank.found:
            print('Tank not Found')
            status = Deviation.TANK_NOT_FOUND

        if self.tank.check_drain and self.read_plc.drain_camera and (self.read_plc.drain_position != self.tank.drain_position):
            print('Drain on Wrong Position')
            status = Deviation.DRAIN_POSITION
        if qnt_stickers > 1:
            print('Found more stickers than needed')
            status = Deviation.STICKER_QUANTITY
        if qnt_stickers > 0 and not self.read_plc.sticker_camera:
            print('Found more stickers than needed')
            status = Deviation.STICKER_QUANTITY
        if self.read_plc.sticker_camera and len(self.tank.stickers) == 0:
            print('Sticker not found')
            status = Deviation.STICKER_NOT_FOUND
        if qnt_stickers:
            sticker = self.tank.stickers[0]
        if self.read_plc.sticker_camera and self.read_plc.sticker != sticker.label_char_index and qnt_stickers:
            print('Wrong Label, expected:' + str(self.read_plc.sticker) + ', received: ' + str(sticker.label))
            self.write_plc.inc_sticker = sticker.label_char_index
            status = Deviation.STICKER_VALUE
        if self.read_plc.sticker_camera and self.read_plc.sticker_angle != sticker.angle and qnt_stickers:
            print('Wrong Label Angle, expected:' + str(self.read_plc.sticker_angle) + ', received: ' + str(sticker.angle))
            self.write_plc.inc_angle = sticker.angle
            status = Deviation.STICKER_ANGLE
        if self.read_plc.sticker_camera and self.read_plc.sticker_position != sticker.quadrant and qnt_stickers:
            print('Wrong Label Position, expected:' + str(self.read_plc.sticker_position) + ', received: ' + str(sticker.quadrant))
            self.write_plc.position_inc_sticker = sticker.quadrant
            status = Deviation.STICKER_POSITION

        self.write_plc.cam_status = int(status)
        self.analyse_counter = self.analyse_counter + 1

        self.__get_final_result(status)


    def __get_final_result(self, status: Deviation):
        self.result_list.append(status)
        print(self.result_list)
        if len(self.result_list) >= self.total_reads:
            if Counter(self.result_list).most_common()[0][0] == 1:
                self.__job_done()
            self.result_list.pop(0)

    def __job_done(self):
        self.final_result = True
        self.write_plc.cam_status = 1
        self.write_plc.job_status = JobStatus.DONE
        self.write_plc.request_ack = False

    def __clear_plc(self) -> None:
        self.write_plc.position_inc_drain = 0
        self.write_plc.position_inc_sticker = 0
        self.write_plc.inc_sticker = 0
        self.write_plc.inc_angle = 0

    def check_skid(self):
        if not self.tank.found and self.read_plc.skid == 0:
            self.abort_job()

    def abort_job(self):
        self.__clear_plc()
        self.write_plc.cam_status = Deviation.TANK_NOT_FOUND
        self.write_plc.job_status = JobStatus.CANCELLED

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

    def new_request(self):
        return self.read_plc.request_number != self.last_request

    def confirm_request(self) -> None:
        print('New Job Request: ', self.read_plc.request_number)
        print(f'SKID: {self.read_plc.skid}, POPID: {self.read_plc.popid}')
        print(f'TANK: {self.read_plc.partnumber} PARAMETER: {self.read_plc.parameter}')
        print(f'STICKER: {self.read_plc.sticker}, ANGLE: {self.read_plc.sticker_angle}, DRAIN: {self.read_plc.drain_position}')
        self.last_request = self.read_plc.request_number
        self.read_plc.read_request = False
        self.write_plc.request_ack = True
        self.write_plc.cam_status = 0
        self.write_plc.job_status = int(JobStatus.RUNNING)
        self.final_result = False
        self.analyse_counter = 0
        self.result_list.clear()
        sleep(1)

    def get_command(self) -> None:
        key = cv.waitKey(1) & 0xFF
        key_pressed(key, self.camera, self.tank)
        if key == ord('n'):
            self.__get_fake_parameters()
        elif key == ord('o'):
            self.__job_done()
        elif key == ord('i'):
            self.__print_plc_values()

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
                _bytearray = self.write_plc.get_bytearray()
                self.plc.write(_bytearray)
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

    def __print_plc_values(self) -> None:
        print('PLC READ:')
        print(self.read_plc.__dict__)
        print('\nPLC WRITE:')
        print(self.write_plc.__dict__)

    def __get_fake_parameters(self) -> None:
        self.read_plc.read_request = True
        self.read_plc.sticker = 1
        self.read_plc.sticker_angle = 2
        self.read_plc.sticker_position = 4
        self.read_plc.drain_position = 0









