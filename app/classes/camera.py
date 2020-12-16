import cv2 as cv
import yaml
import numpy as np
import logging
import platform
from imutils.video.webcamvideostream import WebcamVideoStream
from imutils.video import VideoStream
from models.camera_constants import CameraConstants


if platform.system() == 'Windows':
    from win32api import GetSystemMetrics
class Camera:

    SKIP_FRAMES = 50
    cap = None
    output = None
    enabled = True
    pause = False
    recording = False
    pause = False
    frame_counter = 0
    current_frame = 0
    window_name = 'Main'
    multiple_monitors = False
    monitor_counter = 0
    frame: np.ndarray

    def __init__1(self, config=None):
        self.load_config(config)
        if platform.system() == 'Windows':
            if GetSystemMetrics(CameraConstants.MONITOR_SIZE.value) > self.MONITOR_LIMIT:
                self.multiple_monitors = True

    def __init__(self, config='config.yml'):
        self.load_config_2(config)

    def load_config_2(self, config_file="config.yml"):
        with open(config_file) as file:
            config = yaml.safe_load(file)['camera']
        self.debug = config['debug']
        self.width = config['resolution'][0]
        self.height = config['resolution'][1]
        self.display = config['display']
        self.rpi_camera = config['rpi_camera']
        self.fps = config['fps']
        self.src = config['src']
        self.brighteness = config['brighteness']
        self.contrast = config['contrast']
        self.saturation = config['saturation']
        self.sharpness = config['sharpness']
        self.exposure = config['exposure']
        self.white_balance = config['white_balance']
        self.threaded = config['threaded']
        self.monitor_display = tuple(config['display'])


    def load_config(self, config):
        self.config = config
        self.fps = int(config["FPS"])
        self.width = int(config["WIDTH"])
        self.height = int(config["HEIGHT"])
        self.DISPLAY_WIDTH = int(config["DISPLAY_WIDTH"])
        self.DISPLAY_HEIGHT = int(config["DISPLAY_HEIGHT"])
        self.PRC_CENTER_X_OFFSET = float(config["PRC_CENTER_X_OFFSET"])
        self.PRC_ROI_X_START = float(config["PRC_ROI_X_START"])
        self.PRC_ROI_X_END = float(config["PRC_ROI_X_END"])
        self.PRC_ROI_Y_START = float(config["PRC_ROI_Y_START"])
        self.PRC_ROI_Y_END = float(config["PRC_ROI_Y_END"])
        self.MONITOR_LIMIT = int(self.config['MONITOR_LIMIT'])
        self.MAX_MONITORS = int(self.config['MAX_MONITORS'])

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

    def start(self, source=cv.CAP_DSHOW):
        if self.rpi_camera:
            res = tuple(self.resolution)
            self.cap = VideoStream(src=0
                        , usePiCamera=True
                        , resolution=res
                        , framerate=self.fps)
            self.cap.start()
        elif self.threaded:
            self.cap = WebcamVideoStream(source)
            self.set_hardware_threaded()
            self.cap.start()
        else:
            self.cap = cv.VideoCapture(source)
            self.set_hardware()
        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, self.monitor_display)
        if self.multiple_monitors:
            self.move_window(self.MONITOR_LIMIT + 1, 0)

    def stop(self):
        if self.threaded or self.rpi_camera:
            self.cap.stop()
            self.cap.stream.release()
        else:
            self.cap.release()

    def set_hardware(self, **kwargs): # Camera properties
        # self.cap.set(39, False)
        self.cap.set(CameraConstants.WIDTH.value, self.width)
        self.cap.set(CameraConstants.HEIGHT.value, self.height)
        self.cap.set(CameraConstants.BRIGHTNESS.value, self.brighteness) # min: 0 max: 255 increment:1
        self.cap.set(CameraConstants.CONTRAST.value, self.contrast) # min: 0 max: 255 increment:1
        self.cap.set(CameraConstants.SATURATION.value, self.saturation) # min: 0 max: 255 increment:1
        self.cap.set(CameraConstants.HUE.value, 255) # hue
        # self.cap.set(GAIN, 62)  # min: 0 max: 127 increment:1
        self.cap.set(CameraConstants.EXPOSURE.value, self.exposure) # min: -7 max: -1 increment:1
        self.cap.set(CameraConstants.WHITE_BALANCE.value, self.white_balance) # min: 4000 max: 7000 increment:1
        self.cap.set(CameraConstants.FOCUS.value, 0)  # focus          min: 0   , max: 255 , increment:5

    def set_hardware_threaded(self, **kwargs): # Camera properties
        # self.cap.set(39, False)
        self.cap.stream.set(CameraConstants.WIDTH.value, self.width)
        self.cap.stream.set(CameraConstants.HEIGHT.value, self.height)
        self.cap.stream.set(CameraConstants.BRIGHTNESS.value, self.brighteness) # min: 0 max: 255 increment:1
        self.cap.stream.set(CameraConstants.CONTRAST.value, self.contrast) # min: 0 max: 255 increment:1
        self.cap.stream.set(CameraConstants.SATURATION.value, self.saturation) # min: 0 max: 255 increment:1
        self.cap.stream.set(CameraConstants.HUE.value, 255) # hue
        # self.cap.stream.set(GAIN, 62)  # min: 0 max: 127 increment:1
        self.cap.stream.set(CameraConstants.EXPOSURE.value, self.exposure) # min: -7 max: -1 increment:1
        self.cap.stream.set(CameraConstants.WHITE_BALANCE.value, self.white_balance) # min: 4000 max: 7000 increment:1
        self.cap.stream.set(CameraConstants.FOCUS.value, 0)  # focus          min: 0   , max: 255 , increment:5

    def move_window(self, x, y):
        if self.MAX_MONITORS == 2:
            logging.info(f'Moving window to {x}, {y}')
            cv.moveWindow(self.window_name, x, y)

    def write_on_image(self):
        pass

    def show(self, main_frame: np.ndarray=0):
        cv.imshow(self.window_name, self.cap.read())
        cv.waitKey(1) & 0xFF

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

    def update_frame_counter(self):
        if self.frame_counter % 200 == 0:
            logging.info("Keep Alive Camera Message")

        self.frame_counter = self.frame_counter + \
            1 if not self.pause else self.frame_counter
        self.frame_counter = 0 if self.frame_counter >= 1000 else self.frame_counter

    def read(self):
        if self.threaded:
            return True, self.cap.read()
        return self.cap.read()

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
