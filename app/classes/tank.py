from numpy.core.defchararray import lower
import yaml
from typing import List
import numpy as np
import cv2 as cv
from .sticker import Sticker
from .drain import Drain
from .tf_model import TFModel
from .colors import *

font = cv.FONT_HERSHEY_SIMPLEX


class Tank:

    found = False
    image: np.ndarray = 0
    x, y, w, h = 0, 0, 0, 0
    circle: List[int] = []
    radius = 0
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
        width, height = config["size"]
        self.min_width = width[0]
        self.max_width = width[1]
        self.min_height = height[0]
        self.max_height = height[1]
        self.min_radius = config['min_radius']
        self.min_dist = config['min_radius']
        self.params = config['params']
        self.table_hsv = config['table_filter']

    def load_sticker_config(self, config):
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

    def get_tank_image(self, frame: np.ndarray):
        self.color_image = frame[self.y: self.y +
                                 self.h, self.x: self.x + self.w, :]
        return self.color_image

    def find_in_circle(self, frame: np.ndarray):
        g_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(g_frame, (5,5), 0)

        # blur = cv.GaussianBlur(g_frame, (5,5), 0)
        # test with X ROI
        # cam_config = self.config["camera"]
        # height, width = g_frame.shape
        # roi = cam_config["roi"]
        # off1 = int(roi["x"][0] * width // 100)
        # off2 = int(roi["x"][1] * width // 100)
        # crop_mask = np.ones((width, height), np.uint8)

        # croped_img = cv.bitwise_and(g_frame, g_frame, mask=crop_mask)

        # find only inside the roi lines to reduce error
        self.circles = cv.HoughCircles(blur, cv.HOUGH_GRADIENT, 1.2,
                                        param1=self.params[0],
                                        param2=self.params[1],
                                        minDist=self.min_dist,
                                        minRadius=self.min_radius)  # parametrizar o segundo valor
        if self.circles is not None:
            circles = np.uint16(np.around(self.circles))
            for x, y, r in circles[0, :]:
                self.x = int(x - r) if (x - r) > 0 else 0
                self.y = int(y - r) if (y - r) > 0 else 0
                self.w, self.h = 2*r, 2*r
                self.found = True
                self.image = frame[self.y: self.y +
                                   self.h, self.x: self.x + self.w]
        else:
            self.found = False
            self.x, self.y, self.w, self.h = 0, 0, 0, 0

    def find(self, frame: np.ndarray):

        cam_config = self.config["camera"]
        c_width, c_height = cam_config["resolution"]
        roi = cam_config["roi"]
        y_offset_start = int(c_height * roi["y"][0] // 100)
        y_offset_end = int(c_height * roi["y"][1] // 100)

        image = frame.copy()
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        image[:y_offset_start, :] = 255

        image = cv.blur(image, (9, 9), cv.BORDER_WRAP)
        _, image = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

        mid_x = image.shape[1] // 2
        mid_y = image.shape[0] // 2

        # Search for the central line (in pink) and count the black pixel quantity

        x_center_offset = int(cam_config["center_x_offset"] * c_width // 100)
        vector_y = image[:, mid_x + x_center_offset]
        roi_vector_y = vector_y[y_offset_start:y_offset_end]
        roi_vector_y = roi_vector_y[roi_vector_y == 0]

        if roi_vector_y.size > int(self.min_height):
            self.h = roi_vector_y.size
        else:
            self.h = 0
            self.found = False
            return False

        self.y = np.where(vector_y == 0)[0][0]  # Get the first black pixel

        center_y = (self.y + self.h) // 2
        off1 = int(roi["x"][0] * c_width // 100)
        off2 = int(roi["x"][1] * c_width // 100)

        adj_y1 = int(self.y + (self.h * 0.22))  # SET IN CONFIG
        adj_y2 = int(center_y + (self.h * 0.3))

        # Create lines for adj_y
        vector_x1 = image[adj_y1, off1:mid_x]
        vector_x2 = image[adj_y2, mid_x:off2]

        for i in range(len(vector_x1)):
            if vector_x1[i] == 0:
                self.x = i + off1
                break

        vector_x2 = image[adj_y2, mid_x:off2]

        for i in range(len(vector_x2) - 1, -1, -1):
            if vector_x2[i] == 0:
                x2 = mid_x - i
                self.w = (image.shape[1] - self.x) - x2
                break

        self.found = self.h >= self.min_height
        self.image = frame[self.y: self.y + self.h, self.x: self.x + self.w]

    # merge into the other method
    def get_sticker_position_lab(self, frame: np.ndarray):

        if self.x <= 0:
            tank = frame.copy()
            return
        else:
            tank = frame[self.y: self.y + self.h, self.x: self.x + self.w]

        if tank.size == 0:
            return

        kernel = np.ones((5, 5), np.uint8)  # GET the kernel from config
        lab = cv.cvtColor(tank, cv.COLOR_BGR2LAB)
        lower = np.array(self.sticker_lab[0], np.uint8)
        higher = np.array(self.sticker_lab[1], np.uint8)
        mask = cv.inRange(lab, lower, higher)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel, iterations=2)
        contour, _ = cv.findContours(
            mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        self.append_stickers(contour, tank)

        if self.debug_sticker:
            cv.imshow("debug_tank_sticker", mask)

    def get_sticker_position(self, frame: np.ndarray):
        g_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        tank = g_frame[self.y: self.y + self.h, self.x: self.x + self.w]
        # Get kernel from config
        _, thresh = cv.threshold(tank, self.sticker_thresh, 255, cv.THRESH_BINARY)
        blur = cv.blur(thresh, (5, 5), cv.BORDER_CONSTANT) # test updated
        contour, hier = cv.findContours(blur, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        self.append_stickers(contour, tank)
        if self.debug_sticker:
            cv.imshow("debug_tank_sticker", thresh)

    def append_stickers(self, contour, tank):
        camera = self.config['camera']['number']
        self.stickers = []
        for c in contour:
            area = cv.contourArea(c)
            cond = area >= self.sticker_area["min"]
            cond = cond and area <= self.sticker_area["max"]
            if cond:
                arc = cv.arcLength(c, True)
                poly = cv.approxPolyDP(c, arc * 0.02, True)
                if len(poly) == 4:
                    (x, y, w, h) = cv.boundingRect(c)
                    ar = w / float(h)
                    cond = ar >= 0.8 and ar <= 1.2
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

    def get_drain_2(self, frame: np.ndarray, mode='lab', rgb=False):

        self.drain_found = False
        self.drain_area_found = 0
        self.drain_position = 0
        self.drain_x, self.drain_y, self.drain_w, self.drain_h = 0, 0, 0, 0
        cam_config = self.config["camera"]
        c_width, c_height = cam_config["resolution"]
        roi = cam_config["roi"]
        crop_mask = np.ones((c_height, c_width), np.uint8)
        crop_mask[:, 0: self.x + 10] = 0
        crop_mask[:, self.x + self.w - 10:] = 0
        croped_img = cv.bitwise_and(frame, frame, mask=crop_mask)
        _filter: np.ndarray = 0

        if mode == 'lab':
            # _filter = cv.cvtColor(croped_img, cv.COLOR_BGR2LAB)  # LAB
            scheme = cv.COLOR_RGB2LAB if rgb else cv.COLOR_BGR2LAB
            _filter = cv.cvtColor(croped_img, scheme)  # LAB
            lower = np.array(self.drain_lab[0], np.uint8)
            higher = np.array(self.drain_lab[1], np.uint8)
        else:
            scheme = cv.COLOR_RGB2HSV if rgb else cv.COLOR_BGR2HSV
            _filter = cv.cvtColor(croped_img, cv.COLOR_BGR2HSV)  # HSV
            lower = np.array(self.drain_hsv[0], np.uint8)
            higher = np.array(self.drain_hsv[1], np.uint8)

        blur = cv.GaussianBlur(_filter, self.drain_blur, 1)

        mask = cv.inRange(blur, lower, higher)
        kernel = np.ones(self.drain_kernel, np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel, iterations=2)

        if self.debug_drain:
            cv.imshow("debug_drain", mask)

        cnt, _ = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        sorted_cnts = sorted(cnt, key=lambda cnt: cv.contourArea(cnt))

        if len(sorted_cnts):
            c = sorted_cnts[-1]
            area = cv.contourArea(c)
            cond = area >= self.drain_area["min"]
            cond = cond and area <= self.drain_area["max"]
            if cond:
                (x, y, w, h) = cv.boundingRect(c)
                self.drain_found = True
                self.drain = Drain(x, y, w, h, area)
                self.drain_x, self.drain_y, self.drain_w, self.drain_h = x, y, w, h
                zero_x = self.x + (self.w // 2)
                zero_y = self.y + (self.h // 2)
                self.drain_rel_x = x - zero_x + (w // 2)
                self.drain_rel_y = (-1) * (y - zero_y) - (h // 2)
                self.drain_area_found = area
                row, col = -1, -1
                quad_list = [[6, 7, 8], [9, 10, 11], [12, 13, 14]]
                temp_x = (x - self.x) / self.w
                temp_y = (y - self.y) / self.h
                if temp_x <= 0.3:
                    col = 0
                elif temp_x >= 0.3 and temp_x <= 0.7:
                    col = 1
                elif temp_x > 0.7:
                    col = 2
                if temp_y <= 0.2:
                    row = 0
                elif temp_y >= 0.2 and temp_y <= 0.92:
                    row = 1
                elif temp_y > 0.92:
                    row = 2
                self.drain_position = quad_list[row][col]

    def get_drain_ml(self, frame: np.ndarray, model: TFModel):
        # cam_config = self.config["camera"]
        # c_width, c_height = cam_config["resolution"]
        # roi = cam_config["roi"]
        # crop_mask = np.ones((c_height, c_width), np.uint8)
        # crop_mask[:, 0: self.x + 10] = 0
        # crop_mask[:, self.x + self.w - 10:] = 0
        # croped_img = cv.bitwise_and(frame, frame, mask=crop_mask)
        if self.found and self.x > 10 and self.y > 10:
            tank = frame[self.y - 10 :self.y + self.h, self.x -10: self.x+self.w]
            index, label = model.predict(tank)
            self.drain_position = int(label)
        else:
            self.drain_position = 0


    def get_drain(self, frame: np.ndarray):  # merge into another method

        cam_config = self.config["camera"]
        c_width, c_height = cam_config["resolution"]
        roi = cam_config["roi"]
        # y_offset_start = c_height * roi["y"][0] // 100
        # y_offset_end = c_height * roi["y"][1] // 100
        crop_mask = np.ones((c_height, c_width), np.uint8)

        # Corta as laterais
        crop_mask[:, 0: self.x + 10] = 0
        crop_mask[:, self.x + self.w - 10:] = 0

        # Eixo Y
        crop_mask[0: int(self.y - (self.h * 0.17)), :] = 0

        # Cortar o centro mais % para cima e para baixo
        y_center = self.y + (self.h // 2)
        crop_mask[int(y_center - self.h * 0.4)
                      : int(y_center + self.h * 0.34), :] = 0

        croped_img = cv.bitwise_and(frame, frame, mask=crop_mask)

        hsv = cv.cvtColor(croped_img, cv.COLOR_BGR2HSV)

        blur_kernel = self.drain_blur

        blur = cv.GaussianBlur(hsv, blur_kernel, 1)
        lower = np.array(self.drain_hsv[0], np.uint8)
        higher = np.array(self.drain_hsv[1], np.uint8)
        mask = cv.inRange(blur, lower, higher)

        kernel_open = np.ones(self.DRAIN_FILTER_OPEN, np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel_open, iterations=2)

        if self.debug_drain:
            cv.imshow("debug_drain", mask)

        cnt, hier = cv.findContours(
            mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        self.drain_found = False
        self.drain_area_found = 0
        self.drain_x, self.drain_y, self.drain_w, self.drain_h = 0, 0, 0, 0

        for c in cnt:
            area = cv.contourArea(c)
            (x, y, w, h) = cv.boundingRect(c)
            cond = area >= self.drain_area["min"]
            cond = cond and area < self.drain_area["max"]
            if cond:
                self.drain_found = True
                self.drain_x, self.drain_y, self.drain_w, self.drain_h = x, y, w, h
                zero_x = self.x + self.w // 2
                zero_y = self.y + self.h // 2
                self.drain_rel_x = x - zero_x + (w // 2)
                self.drain_rel_y = (-1) * (y - zero_y) - (h // 2)
                self.drain_area_found = area

    def get_drain_lab(self, frame: np.ndarray):

        cam_config = self.config["camera"]
        c_width, c_height = cam_config["resolution"]
        roi = cam_config["roi"]
        # y_offset_start = c_height * roi["y"][0] // 100
        # y_offset_end = c_height * roi["y"][1] // 100
        crop_mask = np.ones((c_height, c_width), np.uint8)

        # Remove as Laterais
        crop_mask[:, 0: self.x + 10] = 0
        crop_mask[:, self.x + self.w - 10:] = 0

        # Eixo Y
        # crop_mask[0: int(self.y - (self.h * 0.10)), :] = 0

        # Cortar o centro mais % para cima e para baixo (ver possibilidade)
        # y_center = self.y + (self.h // 2)
        # crop_mask[int(y_center - self.h * 0.4) : int(y_center + self.h * 0.34), :] = 0

        croped_img = cv.bitwise_and(frame, frame, mask=crop_mask)

        lab = cv.cvtColor(croped_img, cv.COLOR_BGR2LAB)  # LAB
        hsv = cv.cvtColor(croped_img, cv.COLOR_BGR2HSV)  # HSV
        blur = cv.GaussianBlur(lab, self.drain_blur, 1)

        # TEST WITH HSV FILTER ADD

        lower = np.array(self.drain_hsv[0], np.uint8)
        higher = np.array(self.drain_hsv[1], np.uint8)
        hsv_mask = cv.inRange(hsv, lower, higher)

        # --------------------------

        lower = np.array(self.drain_lab[0], np.uint8)
        higher = np.array(self.drain_lab[1], np.uint8)
        lab_mask = cv.inRange(blur, lower, higher)

        # mask = lab_mask + hsv_mask -- Aditive
        # mask = cv.bitwise_and(lab_mask, hsv_mask)  # subtrative
        mask = lab_mask  # just lab

        kernel = np.ones(self.drain_kernel, np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel, iterations=2)

        if self.debug_drain:
            cv.imshow("debug_drain", mask)
            cv.imshow("debug_drain_lab", lab_mask)
            cv.imshow("debug_drain_hsv", hsv_mask)

        cnt, _ = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        self.drain_found = False
        self.drain_area_found = 0
        self.drain_position = 0
        self.drain_x, self.drain_y, self.drain_w, self.drain_h = 0, 0, 0, 0

        sorted_cnts = sorted(cnt, key=lambda cnt: cv.contourArea(cnt))

        if len(sorted_cnts):
            c = sorted_cnts[-1]
            area = cv.contourArea(c)
            cond = False
            cond = area >= self.drain_area["min"]
            cond = cond and area <= self.drain_area["max"]
            if cond:
                self.drain_found = True
                (x, y, w, h) = cv.boundingRect(c)
                self.drain_x, self.drain_y, self.drain_w, self.drain_h = x, y, w, h
                zero_x = self.x + self.w // 2
                zero_y = self.y + self.h // 2
                self.drain_rel_x = x - zero_x + (w // 2)
                self.drain_rel_y = (-1) * (y - zero_y) - (h // 2)
                self.drain_area_found = area
                row, col = -1, -1
                quad_list = [[6, 7, 8], [9, 10, 11], [12, 13, 14]]
                temp_x = (x - self.x) / self.w
                temp_y = (y - self.y) / self.h
                if temp_x <= 0.3:
                    col = 0
                elif temp_x >= 0.3 and temp_x <= 0.7:
                    col = 1
                elif temp_x > 0.7:
                    col = 2
                if temp_y <= 0.2:
                    row = 0
                elif temp_y >= 0.2 and temp_y <= 0.92:
                    row = 1
                elif temp_y > 0.92:
                    row = 2
                self.drain_position = quad_list[row][col]

    def find_2(self, frame: np.ndarray):

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # hsv = cv.cvtColor(frame, cv.COLOR_RGB2HSV)
        blur = cv.GaussianBlur(hsv,(7,7), 0)
        # blur = cv.medianBlur(hsv, (5,5))
        lower =  np.array( (self.table_hsv[0][0], self.table_hsv[0][1], self.table_hsv[0][2]), np.uint8)
        higher = np.array( (self.table_hsv[1][0], self.table_hsv[1][1], self.table_hsv[1][2]), np.uint8)
        mask = cv.inRange(blur, lower, higher)

        if self.debug_tank:
            cv.imshow('debug_tank', mask)

        cam_config = self.config["camera"]
        c_width, c_height = cam_config["resolution"]
        roi = cam_config["roi"]

        mid_x = frame.shape[1] // 2
        x_center_offset = int(cam_config["center_x_offset"] * c_width // 100)
        vector_y = mask[:, mid_x + x_center_offset]
        roi_vector_y = vector_y[:]
        roi_vector_y = roi_vector_y[roi_vector_y == 0]

        if roi_vector_y.size > int(self.min_height):
            self.h = roi_vector_y.size
        else:
            self.h = 0
            self.found = False
            return False

        self.y = np.where(vector_y == 0)[0][0]  # Get the first black pixel

        center_y = (self.y + self.h) // 2
        off1 = int(roi["x"][0] * c_width // 100)
        off2 = int(roi["x"][1] * c_width // 100)

        adj_y1 = int(self.y + (self.h * 0.22))  # SET IN CONFIG
        adj_y2 = int(center_y + (self.h * 0.3))

        # Create lines for adj_y
        vector_x1 = mask[adj_y1, off1:mid_x]
        vector_x2 = mask[adj_y2, mid_x:off2]

        for i in range(len(vector_x1)):
            if vector_x1[i] == 0:
                self.x = i + off1
                break

        vector_x2 = mask[adj_y2, mid_x:off2]

        for i in range(len(vector_x2) - 1, -1, -1):
            if vector_x2[i] == 0:
                x2 = mid_x - i
                self.w = (mask.shape[1] - self.x) - x2
                break

        self.found = self.h >= self.min_height
        self.image = frame[self.y: self.y + self.h, self.x: self.x + self.w]


