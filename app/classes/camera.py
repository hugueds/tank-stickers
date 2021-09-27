import cv2 as cv
import yaml
import numpy as np
import logging
import platform
from imutils.video.webcamvideostream import WebcamVideoStream
from imutils.video import VideoStream
from logger import logger

if platform.system() == 'Windows':
    from win32api import GetSystemMetrics

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
    full_screen = True

    def __init__(self, config_file='config.yml') -> None:
        self.config_file = config_file
        self.load_config()

    def load_config(self) -> None:
        with open(self.config_file) as file:
            config = yaml.safe_load(file)['camera']
        self.debug = config['debug']
        self.number = config['number']
        self.width = config['resolution'][0]
        self.height = config['resolution'][1]
        self.display = tuple(config['display'])
        self.center_x_offset = config['center_x_offset']
        self.center_y_offset = config['center_y_offset']
        self.roi = config['roi']
        self.rpi_camera = config['rpi_camera']
        self.fps = config['fps']
        self.src = config['src']
        self.full_screen = config['full_screen']
        self.brightness = config['brightness']
        self.contrast = config['contrast']
        self.saturation = config['saturation']
        self.sharpness = config['sharpness']
        self.exposure = config['exposure']
        self.exposure_comp = config['exposure']
        self.white_balance = config['white_balance']
        self.awb_mode= config['awb_mode']
        self.threaded = config['threaded']
        self.monitor_display = tuple(config['display'])
        self.hue = 0

    def start(self) -> None:
        logger.info('Starting Camera')
        if self.rpi_camera:
            self.cap = VideoStream(
                src=self.src, usePiCamera=True, resolution=(self.width, self.height), framerate=self.fps)
            self.cap.start()
            self.set_hardware_rpi()
        elif self.threaded:
            self.cap = WebcamVideoStream(self.src, name='cam')
            self.cap.start()
            self.set_hardware_threaded()
        else:
            self.cap = cv.VideoCapture(self.src)

        if self.multiple_monitors:
            self.move_window(self.MONITOR_LIMIT + 1, 0)

        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, self.monitor_display)
        if self.full_screen:
            cv.setWindowProperty(self.window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    def stop(self) -> None:
        if self.threaded or self.rpi_camera:
            self.cap.stop()
            self.cap.stream.release()
        else:
            self.cap.release()

    def set_hardware_threaded(self, **kwargs) -> None:
        self.cap.stream.set(cv.CAP_PROP_BRIGHTNESS, self.brightness) # # min: 0 max: 255 increment:1
        self.cap.stream.set(cv.CAP_PROP_CONTRAST, self.contrast)  # min: 0 max: 255 increment:1
        self.cap.stream.set(cv.CAP_PROP_SATURATION, self.saturation) #  min: 0 max: 255 increment:1
        self.cap.stream.set(cv.CAP_PROP_SHARPNESS, self.sharpness) #  min: 0 max: 255 increment:1

    def set_hardware_rpi(self) -> None:
        self.cap.stream.camera.iso = 640 # 100, 200, 320, 400, 500, 640, 800.
        self.cap.stream.camera.awb_mode = self.awb_mode
        self.cap.stream.camera.exposure_mode = 'off' # snow, beach, spotlight
        self.cap.stream.camera.exposure_compensation = self.__scale(self.exposure_comp, -25, 25)
        self.cap.stream.camera.brightness = self.__scale(self.brightness, 0, 100)
        self.cap.stream.camera.contrast = self.__scale(self.contrast, -100 , 100)
        self.cap.stream.camera.saturation = self.__scale(self.saturation, -100, 100)
        self.cap.stream.camera.sharpness = self.__scale(self.sharpness, -100, 100)

    def __scale(self, x, y0, y1) -> int:
        x0, x1 = 0, 255
        return int(y0 + ( (y1 -y0) / (x1 - x0) * (x - x0)) )

    def show(self, frame: np.ndarray = np.ones((400, 400, 1))):
        frame = cv.resize(frame, self.display)
        cv.imshow(self.window_name, frame)
        self.__update_frame_counter()

    def move_window(self, x, y) -> None:
        if self.MAX_MONITORS == 2:
            logging.info(f'Moving window to {x}, {y}')
            cv.moveWindow(self.window_name, x, y)

    def __update_frame_counter(self) -> None:
        if self.frame_counter % 200 == 0:
            logging.info("Keep Alive Camera Message")
        self.frame_counter = self.frame_counter + \
            1 if not self.pause else self.frame_counter
        self.frame_counter = 0 if self.frame_counter >= 1000 else self.frame_counter

    def read(self):
        if self.threaded:
            return True, self.cap.read()
        return self.cap.read()

    def get_tune_point(self, frame, x, y):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        return gray[y,x]

    def auto_tune(self, pixel):
        # set contrast, bright and threshold
        if pixel <= 120:
            pass
        elif pixel>=180:
            pass
        elif pixel >=220:
            pass

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
