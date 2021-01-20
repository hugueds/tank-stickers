import yaml
from typing import List
import numpy as np
import cv2 as cv
from classes.sticker import Sticker
from .drain import Drain
from .tf_model import TFModel
from .colors import *

font = cv.FONT_HERSHEY_SIMPLEX

class Tank:

    found = False
    image: np.ndarray = 0
    x, y, w, h = 0, 0, 0, 0
    circle: List[int] = []
    sticker_count = 0
    stickers: List[Sticker] = []
    quantity = 0
    sticker_quadrant = 0
    drain: Drain
    drain_found = False
    drain_position: int = 0
    drain_x, drain_y, drain_w, drain_h = 0, 0, 0, 0
    drain_rel_x, drain_rel_y = 0, 0
    debug_tank = False
    debug_sticker = False
    debug_drain = False

    def __init__(self, config_file="config.yml"):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        with open(self.config_file) as file:
            config = yaml.safe_load(file)
        self.config = config
        self.load_tank_config(config['tank'])
        self.load_sticker_config(config["sticker"])
        self.load_drain_config(config["drain"])

    def load_tank_config(self, config):
        self.weight = {"min": config["min"], "max": config["max"]}
        self.blur = config['blur']
        self.threshold = config['threshold']
        width, height = config["size"]
        self.min_width = width[0]
        self.max_width = width[1]
        self.min_height = height[0]
        self.max_height = height[1]
        self.radius = config['radius']
        self.min_dist = config['min_dist']
        self.params = config['params']
        self.table_hsv = config['table_filter']
        self.check_drain = config['check_drain']

    def load_sticker_config(self, config):
        self.sticker_kernel = config["kernel"]
        self.sticker_thresh = config["threshold"]
        self.sticker_size = config["size"]
        self.sticker_area = config["area"]
        self.sticker_hsv = config["hsv_filter"]
        self.sticker_lab = config["lab_filter"]

    def load_drain_config(self, config):
        self.drain_blur = tuple(config["blur"])
        self.drain_kernel = config["kernel"]
        self.drain_hsv = config["hsv_filter"]
        self.drain_lab = config["lab_filter"]
        self.drain_area = config["area"]
        self.arc = config["arc"]
        self.drain_area_found = 0

    def find_in_circle(self, frame: np.ndarray, _filter='threshold'):

        # TODO: Use HSV / LAB Filter

        g_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ys, ye, xs, xe = self.get_roi(frame)
        g_frame = self.__eliminate_non_roi(g_frame, ys, ye, xs, xe)


        if _filter == 'threshold':
            blur = cv.blur(g_frame, tuple(self.blur), 0)
            _, mask = cv.threshold(blur, self.threshold, 255, cv.THRESH_BINARY)
        else:
            if _filter == 'hsv':
                cvt_frame = cv.cvtColor(frame, cv.COLOR_RGB2HSV)
                lower =  np.array( (self.table_hsv[0][0], self.table_hsv[0][1], self.table_hsv[0][2]), np.uint8)
                higher = np.array( (self.table_hsv[1][0], self.table_hsv[1][1], self.table_hsv[1][2]), np.uint8)
            else:
                cvt_frame = cv.cvtColor(frame, cv.COLOR_RGB2LAB)
                lower =  np.array( (self.table_hsv[0][0], self.table_hsv[0][1], self.table_hsv[0][2]), np.uint8)
                higher = np.array( (self.table_hsv[1][0], self.table_hsv[1][1], self.table_hsv[1][2]), np.uint8)
            mask = cv.inRange(cvt_frame, lower, higher)

        # mask = cv.erode(mask, None, iterations=2)
        # mask = cv.dilate(mask, None, iterations=4)

        if self.debug_tank:
            cv.imshow('debug_tank', mask)

        self.circles = cv.HoughCircles(mask, cv.HOUGH_GRADIENT,
                                        param1=self.params[0],
                                        param2=self.params[1],
                                        minDist=self.min_dist,
                                        dp= self.radius[0],
                                        minRadius=self.radius[1],
                                        maxRadius=self.radius[2])
        self.found = False
        self.x, self.y, self.w, self.h = 0, 0, 0, 0
        if self.circles is not None:
            circles = np.uint16(np.around(self.circles))
            for x, y, r in circles[0, :]:
                self.x = int(x - r) if (x - r) > 0 and x < frame.shape[1] else 0
                self.y = int(y - r) if (y - r) > 0 and y < frame.shape[0] else 0

                if self.x > 0 and self.y > 0:
                    self.w, self.h = 2*r, 2*r
                    self.found = True
                    self.image = frame[self.y: self.y + self.h, self.x: self.x + self.w]

    def find(self, frame: np.ndarray) -> None:

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        blur = cv.GaussianBlur(hsv, tuple(self.blur), 0)
        lower =  np.array( (self.table_hsv[0][0], self.table_hsv[0][1], self.table_hsv[0][2]), np.uint8)
        higher = np.array( (self.table_hsv[1][0], self.table_hsv[1][1], self.table_hsv[1][2]), np.uint8)
        mask = cv.inRange(blur, lower, higher)

        ys, ye, x_off_start, x_off_end = self.get_roi(frame)
        mask = self.__eliminate_non_roi(mask, ys, ye, x_off_start, x_off_end)

        # morph close

        if self.debug_tank:
            cv.imshow('debug_tank', mask)

        cam_config = self.config['camera']
        mid_x = frame.shape[1] // 2
        x_center_offset = int(cam_config["center_x_offset"] * frame.shape[1] // 100)
        vector_y = mask[:, mid_x + x_center_offset]
        roi_vector_y = vector_y[:]
        roi_vector_y = roi_vector_y[roi_vector_y == 0]

        if roi_vector_y.size > int(self.min_height):
            self.h = roi_vector_y.size
        else:
            self.h = 0
            self.found = False
            return

        self.y = np.where(vector_y == 0)[0][0]  # Get the first black pixel

        center_y = (self.y + self.h) // 2

        adj_y1 = int(self.y + (self.h * 0.22))  # SET IN CONFIG
        adj_y2 = int(center_y + (self.h * 0.3))

        # Create lines for adj_y
        vector_x1 = mask[adj_y1, x_off_start:mid_x]
        vector_x2 = mask[adj_y2, mid_x:x_off_end]

        for i in range(len(vector_x1)):
            if vector_x1[i] == 0:
                self.x = i + x_off_start
                break

        vector_x2 = mask[adj_y2, mid_x:x_off_end]

        for i in range(len(vector_x2) - 1, -1, -1):
            if vector_x2[i] == 0:
                x2 = mid_x - i
                self.w = (mask.shape[1] - self.x) - x2
                break

        self.found = self.h >= self.min_height and self.w >= self.min_width
        self.image = frame[self.y: self.y + self.h, self.x: self.x + self.w]

    def find_2(self, frame: np.ndarray):

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        blur = cv.blur(hsv, tuple(self.blur), 0)
        lower =  np.array( (self.table_hsv[0][0], self.table_hsv[0][1], self.table_hsv[0][2]), np.uint8)
        higher = np.array( (self.table_hsv[1][0], self.table_hsv[1][1], self.table_hsv[1][2]), np.uint8)
        mask = cv.inRange(blur, lower, higher)

        ys, ye, x_off_start, x_off_end = self.get_roi(frame)
        mask = self.__eliminate_non_roi(mask, ys, ye, x_off_start, x_off_end)

        if self.debug_tank:
            cv.imshow('debug_tank', mask)

        cam_config = self.config['camera']
        mid_x = frame.shape[1] // 2

        x_center_offset = int(cam_config["center_x_offset"] * frame.shape[1] // 100)
        vector_y = mask[:, mid_x + x_center_offset]
        roi_vector_y = vector_y[:]
        roi_vector_y = roi_vector_y[roi_vector_y == 0]

        if roi_vector_y.size > int(self.min_height):
            self.h = roi_vector_y.size
        else:
            self.w = 0
            self.h = 0
            self.found = False
            return

        self.y = np.where(vector_y == 0)[0][0]  # Get the first black pixel

        mid_y = frame.shape[0] // 2
        y_center_offset = int(cam_config["center_y_offset"] * frame.shape[0] // 100)
        vector_x = mask[mid_y + y_center_offset, :]
        roi_vector_x = vector_x[:]
        roi_vector_x = roi_vector_x[roi_vector_x == 0]

        self.w = roi_vector_x.size
        self.x = np.where(vector_x == 0)[0][0]  # Get the first black pixel

        self.found = self.h >= self.min_height and self.w >= self.min_width
        self.image = frame[self.y: self.y + self.h, self.x: self.x + self.w]

    def get_sticker_position(self, frame: np.ndarray):
        if self.x <= 0:
            tank = frame.copy()
            return
        else:
            tank = frame[self.y: self.y + self.h, self.x: self.x + self.w]
        if tank.size == 0:
            return

        kernel = np.ones(self.sticker_kernel, np.uint8)
        g_frame = cv.cvtColor(tank, cv.COLOR_BGR2GRAY)
        _, th = cv.threshold(g_frame, self.sticker_thresh, 255, cv.THRESH_BINARY)
        # mask = cv.morphologyEx(th, cv.MORPH_CLOSE, kernel, iterations=3)
        mask = cv.erode(th, None, iterations=3)
        mask = cv.dilate(mask, None, iterations=5)
        self.append_stickers(mask, tank)

        if self.debug_sticker:
            cv.imshow("debug_tank_sticker", mask)

    def get_sticker_position_lab(self, frame: np.ndarray):

        if self.x <= 0:
            tank = frame.copy()
            return
        else:
            tank = frame[self.y: self.y + self.h, self.x: self.x + self.w]

        if tank.size == 0:
            return

        kernel = np.ones(self.sticker_kernel, np.uint8)
        lab = cv.cvtColor(tank, cv.COLOR_BGR2LAB)
        lower = np.array(self.sticker_lab[0], np.uint8)
        higher = np.array(self.sticker_lab[1], np.uint8)
        mask = cv.inRange(lab, lower, higher)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel, iterations=5) # OLD
        # mask = cv.erode(mask, None, iterations=2)
        # mask = cv.dilate(mask, None, iterations=4)
        self.append_stickers(mask, tank)
        if self.debug_sticker:
            cv.imshow("debug_tank_sticker", mask)

    def append_stickers(self, mask, tank):
        camera = self.config['camera']['number']
        self.stickers = []
        contour, _ = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        for c in contour:
            area = cv.contourArea(c)
            cond = area >= self.sticker_area["min"]
            cond = cond and area <= self.sticker_area["max"]
            if cond:
                arc = cv.arcLength(c, True)
                poly = cv.approxPolyDP(c, arc * 0.03, True)
                if len(poly) == 4:
                    (x, y, w, h) = cv.boundingRect(c)
                    ar = w / float(h)
                    cond = ar >= 0.75 and ar <= 1.25
                    cond = cond and (h) >= self.sticker_size["min"]
                    cond = cond and (h) <= self.sticker_size["max"]
                    cond = cond and (w) >= self.sticker_size["min"]
                    cond = cond and (w) <= self.sticker_size["max"]
                    if cond:
                        sticker = Sticker(self.x + x, self.y + y, w, h, area)
                        sticker.image = tank[y: y + h, x: x + w]
                        sticker.set_relative(self)
                        sticker.calc_quadrant(self.x, self.y, self.w, self.h, camera)
                        self.stickers.append(sticker)
        self.quantity = len(self.stickers)
        if self.quantity == 1:
            self.sticker_quadrant = self.stickers[0].quadrant
        else:
            self.sticker_quadrant = 99

    def get_drain_ml(self, frame: np.ndarray, model: TFModel):
        self.drain_position = 0
        if self.found:
            y_off_start, y_off_end, x_off_start, x_off_end = self.get_roi(frame)
            croped_img = frame[y_off_start:y_off_end,x_off_start:x_off_end,:]
            index, label = model.predict(croped_img)
            self.drain_position = int(label)

    def get_roi(self, frame: np.ndarray):
        camera_config = self.config['camera']
        c_height, c_width = frame.shape[:2]
        roi = camera_config['roi']
        y_off_start = int(c_height * roi["y"][0] // 100)
        y_off_end = int(c_height * roi["y"][1] // 100)
        x_off_start = int(roi["x"][0] * c_width // 100)
        x_off_end = int(roi["x"][1] * c_width // 100)
        return y_off_start, y_off_end, x_off_start, x_off_end

    def __eliminate_non_roi(self, frame: np.ndarray, ys, ye, xs, xe, color=255):
        frame[0:ys] = color
        frame[ye:frame.shape[0]] = color
        frame[:, 0:xs] = color
        frame[:, xe:frame.shape[1]] = color
        return frame

    def get_tank_image(self, frame: np.ndarray):
        return frame[self.y: self.y + self.h, self.x: self.x + self.w, :]
