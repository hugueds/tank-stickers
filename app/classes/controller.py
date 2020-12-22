import cv2 as cv
import numpy as np
from datetime import datetime
from time import sleep
from threading import Thread
from models import PLCInterface
from classes.tank import Tank, Sticker
from classes.plc import PLC
from classes.camera import Camera
from classes.commands import *
from classes.image_writter import *
from models.app_states import AppState
from classes.tf_model import TFModel


class Controller:


    camera_side = 0 # 0 = Middle, 1 = Right, 2 = Left
    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    plc_interface: PLCInterface
    start_time = datetime.now()
    tank: Tank
    thread_plc: Thread
    thread_camera: Thread
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
        Thread(name='thread_plc', target=self.update_plc, daemon=True).start()

    def set_state(self, state: AppState):
        self.state = state

    def update_plc(self):
        print('Starting PLC Thread')
        self.plc.connect()
        while self.plc.enabled:
            self.plc.read()
            self.plc.write(self.tank)
            sleep(0.2) # PLC Cycle
        else:
            print('PLC is not enabled')

    def save_result(self):
        pass


    def extract_tank(self):        
        if self.camera_side == 0:
            pass
        elif self.camera_side == 1:
            pass
        elif self.camera_side == 2:
            pass
        

    def update_camera_setting(self):
        pass








