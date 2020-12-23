import cv2 as cv
import yaml
import numpy as np
import logging
import platform
from imutils.video.webcamvideostream import WebcamVideoStream
from imutils.video import VideoStream
from models.camera_constants import CameraConstants
from logger import logger

if platform.system() == 'Windows':
    from win32api import GetSystemMetrics

SKIP_FRAMES = 50

class Camera:

    cap = None
    output = None
    enabled = True
    pause = False
    recording = False
    frame_counter = 0
    current_frame = 0
    window_name = 'Main'
    multiple_monitors = False
    monitor_counter = 0    

    def __init__(self, config='config.yml'):
        self.load_config(config)

    def load_config(self, config_file="config.yml"):
        with open(config_file) as file:
            config = yaml.safe_load(file)['camera']
        self.debug = config['debug']
        self.width = config['resolution'][0]
        self.height = config['resolution'][1]
        self.display = config['display']
        self.center_x_offset = config['center_x_offset']
        self.roi = config['roi']
        self.rpi_camera = config['rpi_camera']
        self.fps = config['fps']
        self.src = config['src']
        self.brightness = config['brightness']
        self.contrast = config['contrast']
        self.saturation = config['saturation']
        self.sharpness = config['sharpness']
        self.exposure = config['exposure']
        self.white_balance = config['white_balance']
        self.threaded = config['threaded']
        self.monitor_display = tuple(config['display'])
        self.hue = 0

    def load_hardware_config(self, config):
        self.BRIGHTNESS = int(config["BRIGHTNESS"])
        self.CONTRAST = int(config["CONTRAST"])
        self.SATURATION = int(config["SATURATION"])
        self.HUE = int(config["HUE"])
        self.GAIN = int(config["GAIN"])
        self.EXPOSURE = int(config["EXPOSURE"])
        self.WHITE_BALANCE = int(config["WHITE_BALANCE"])
        self.FOCUS = int(config["FOCUS"])
        self.SHARPNESS = int(config["SHARPNESS"])

    def start(self):
        logger.info('Starting Camera')
        if self.rpi_camera:
            res = tuple(self.resolution)
            self.cap = VideoStream(
                src=self.src, usePiCamera=True, resolution=res, framerate=self.fps)
            self.cap.start()
        elif self.threaded:
            self.cap = WebcamVideoStream(self.src, name='cam', resolution=(self.width, self.height))
            self.cap.start()
            self.set_hardware_threaded()
        else:
            self.cap = cv.VideoCapture(self.src)
            self.set_hardware()

        if self.multiple_monitors:
            self.move_window(self.MONITOR_LIMIT + 1, 0)

        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, self.monitor_display)

    def stop(self):
        if self.threaded or self.rpi_camera:
            self.cap.stop()
            self.cap.stream.release()
        else:
            self.cap.release()

    def set_hardware(self, **kwargs):
        self.cap.set(CameraConstants.WIDTH.value, self.width)
        self.cap.set(CameraConstants.HEIGHT.value, self.height)
        self.cap.set(CameraConstants.BRIGHTNESS.value, self.brighteness)        
        self.cap.set(CameraConstants.CONTRAST.value, self.contrast)        
        self.cap.set(CameraConstants.SATURATION.value, self.saturation)
        self.cap.set(CameraConstants.HUE.value, 255)        
        self.cap.set(CameraConstants.EXPOSURE.value, self.exposure)        
        self.cap.set(CameraConstants.WHITE_BALANCE.value, self.white_balance)        
        self.cap.set(CameraConstants.FOCUS.value, 0)

    def set_hardware_threaded(self, **kwargs):        
        self.cap.stream.set(cv.CAP_PROP_BRIGHTNESS, self.brightness) # # min: 0 max: 255 increment:1
        self.cap.stream.set(cv.CAP_PROP_CONTRAST, self.contrast)  # min: 0 max: 255 increment:1        
        self.cap.stream.set(cv.CAP_PROP_SATURATION, self.saturation) #  min: 0 max: 255 increment:1
        # self.cap.stream.set(cv.CAP_PROP_HUE, self.hue)  # hue
        # self.cap.stream.set(cv.CAP_PROP_GAIN, 127)  # min: 0 max: 127 increment:1
        # self.cap.stream.set(cv.CAP_PROP_EXPOSURE, 0)  # min: -13 max: -1 increment:1
        # # min: 4000 max: 7000 increment:1
        # self.cap.stream.set(cv.CAP_WHITE, self.white_balance)        
        # # focus          min: 0   , max: 255 , increment:5
        # self.cap.stream.set(CameraConstants.FOCUS.value, 0)

    def set_hardware_rpi(self):
        pass

    def show(self, frame: np.ndarray = np.ones((400, 400, 1))):
        cv.imshow(self.window_name, frame)

    def move_window(self, x, y):
        if self.MAX_MONITORS == 2:
            logging.info(f'Moving window to {x}, {y}')
            cv.moveWindow(self.window_name, x, y)

    def write_on_image(self):
        pass

    def update_frame_counter(self):
        if self.frame_counter % 200 == 0:
            logging.info("Keep Alive Camera Message")

        self.frame_counter = self.frame_counter + \
            1 if not self.pause else self.frame_counter
        self.frame_counter = 0 if self.frame_counter >= 1000 else self.frame_counter

    def read(self) -> (bool, np.ndarray):
        if self.threaded:
            return True, self.cap.read()
        return self.cap.read()

    def update(self):
        print('Starting update')

    def set_alpha(self, image):
        # loop over the alpha transparency values
        alpha = 0.5
        beta = (1 - alpha)
        gamma = 0.0
        background = np.zeros((self.height, self.width, 3), np.uint8)
        background[:, :, 1] = 200
        background[:, :, 2] = 200
        added_image = cv.addWeighted(background, alpha, image, beta, gamma)
        return added_image

    def update_window_position(self):
        pass
        # if platform.system() == 'Windows':
        #     if GetSystemMetrics(78) == 3200 and not self.multiple_monitors:
        #         self.multiple_monitors = True
        #         self.move_window(self.MONITOR_LIMIT + 1, 0)
        #     elif GetSystemMetrics(78) <= 1920 and self.multiple_monitors:
        #         self.multiple_monitors = False

        # if self.multiple_monitors and platform.system() == 'Windows':
        #     cv.imshow(self.window_name, main_frame)
        #     if self.monitor_counter == 50:
        #         self.move_window(self.MONITOR_LIMIT + 1, 0)
        #     if self.monitor_counter < 50 + 1:
        #         self.monitor_counter += 1

        # elif platform.system() == 'Linux':
        #     cv.imshow(self.window_name, main_frame)

        # else:
        #     self.monitor_counter = 0
        #     cv.destroyWindow(self.window_name)
