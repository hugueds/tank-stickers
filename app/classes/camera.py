import cv2 as cv
import numpy as np
import classes.colors as colors
import logging
import platform

if platform.system() == 'Windows':
    from win32api import GetSystemMetrics

class Camera:

    MONITOR_IMAGE = (1280, 720)
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

    def __init__(self, config=None):
        self.load_config(config)

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
        self.MAX_MONITORS = 2  # int(self.config['MAX_MONITORS'])
        if platform.system() == 'Windows':
            self.multiple_monitors = True if GetSystemMetrics(
                78) > self.MONITOR_LIMIT else False

    def start(self, cap):
        self.cap = cap
        # self.cap.set(39, False)
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)
        # brightness     min: 0   , max: 255 , increment:1
        self.cap.set(10, 180)
        # contrast       min: 0   , max: 255 , increment:1
        self.cap.set(11, 140)
        # saturation     min: 0   , max: 255 , increment:1
        self.cap.set(12, 255)
        self.cap.set(13, 255)   # hue
        # self.cap.set(14, 62  )  # gain           min: 0   , max: 127 , increment:1
        # exposure       min: -7  , max: -1  , increment:1
        self.cap.set(15, -6)
        # white_balance  min: 4000, max: 7000, increment:1
        self.cap.set(17, 4200)
        self.cap.set(28, 0)  # focus          min: 0   , max: 255 , increment:5
        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, self.MONITOR_IMAGE)
        self.move_window(self.MONITOR_LIMIT + 1, 0)

    def move_window(self, x, y):
        if self.MAX_MONITORS == 2:
            logging.info(f'Moving window to {x}, {y}')
            cv.moveWindow(self.window_name, x, y)

    def show(self, main_frame, other_frames=[]):

        if platform.system() == 'Windows':
            if GetSystemMetrics(78) == 3200 and not self.multiple_monitors:
                self.multiple_monitors = True
                self.move_window(self.MONITOR_LIMIT + 1, 0)
            elif GetSystemMetrics(78) <= 1920 and self.multiple_monitors:
                self.multiple_monitors = False

        if self.multiple_monitors and platform.system() == 'Windows':
            cv.imshow(self.window_name, main_frame)
            if self.monitor_counter == 50:
                self.move_window(self.MONITOR_LIMIT + 1, 0)
            if self.monitor_counter < 50 + 1:
                self.monitor_counter += 1

        elif platform.system() == 'Linux':
            cv.imshow(self.window_name, main_frame)

        else:
            self.monitor_counter = 0
            cv.destroyWindow(self.window_name)

    def update_frame_counter(self):
        if self.frame_counter % 200 == 0:
            logging.info("Keep Alive Camera Message")

        self.frame_counter = self.frame_counter + \
            1 if not self.pause else self.frame_counter
        self.frame_counter = 0 if self.frame_counter >= 1000 else self.frame_counter

    def read(self):
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
