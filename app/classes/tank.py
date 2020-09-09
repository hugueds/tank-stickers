import numpy as np
import cv2 as cv
from .sticker import Sticker
from .colors import *

font = cv.FONT_HERSHEY_SIMPLEX

class Tank:

    found = False       
    image = 0
    x, y, w, h = 0, 0, 0, 0
    sticker_count = 0
    stickers = []
    drain_found = False
    drain_x, drain_y, drain_w, drain_h = 0, 0, 0, 0
    drain_rel_x, drain_rel_y = 0, 0
    drain_area = 0
    debug_tank = False        
    debug_sticker = False
    debug_drain = False    

    def __init__(self, config=None):        
        self.config = config
        self.load_config(config["TANK"])
        self.load_sticker_config(config["STICKER"])
        self.load_drain_config(config["DRAIN"])

    def load_config(self, config):                
        self.MIN_HEIGHT = int(config["MIN_HEIGHT"])
        self.MAX_HEIGHT = int(config["MAX_HEIGHT"])
        self.MIN_WIDTH = int(config["MIN_WIDTH"])
        self.MAX_WIDTH = int(config["MAX_WIDTH"])
        
    def load_sticker_config(self, config):
        self.STICKER_L_LOW = int(config["L_LOW"])
        self.STICKER_L_HIGH = int(config["L_HIGH"])
        self.STICKER_A_LOW = int(config["A_LOW"])
        self.STICKER_A_HIGH = int(config["A_HIGH"])
        self.STICKER_B_LOW = int(config["B_LOW"])
        self.STICKER_B_HIGH = int(config["B_HIGH"])
        self.STICKER_MIN_HEIGHT = int(config["MIN_HEIGHT"])
        self.STICKER_MAX_HEIGHT = int(config["MAX_HEIGHT"])
        self.STICKER_MIN_WIDTH = int(config["MIN_WIDTH"])
        self.STICKER_MAX_WIDTH = int(config["MAX_WIDTH"])
        self.STICKER_MIN_AREA = int(config["MIN_AREA"])
        self.STICKER_MAX_AREA = int(config["MAX_AREA"])
        self.STICKER_MODEL_SIZE = int(config["MODEL_SIZE"])

    def load_drain_config(self, config):
        self.DRAIN_FILTER_BLUR = tuple(map(int, config["FILTER_BLUR"].split(',')))
        self.DRAIN_FILTER_KERNEL = tuple(map(int, config["FILTER_KERNEL"].split(',')))
        self.DRAIN_ARC_MIN = int(config['ARC_MIN'])
        self.DRAIN_AREA_MIN = int(config['AREA_MIN'])
        self.DRAIN_AREA_MAX = int(config['AREA_MAX'])
        self.DRAIN_LAB_L_LOW = int(config['L_LOW'])
        self.DRAIN_LAB_L_HIGH = int(config['L_HIGH'])
        self.DRAIN_LAB_A_LOW = int(config['A_LOW'])
        self.DRAIN_LAB_A_HIGH = int(config['A_HIGH'])
        self.DRAIN_LAB_B_LOW = int(config['B_LOW'])
        self.DRAIN_LAB_B_HIGH = int(config['B_HIGH'])
        self.DRAIN_HSV_H_LOW = int(config['H_LOW'])
        self.DRAIN_HSV_H_HIGH = int(config['H_HIGH'])
        self.DRAIN_HSV_S_LOW = int(config['S_LOW'])
        self.DRAIN_HSV_S_HIGH = int(config['S_HIGH'])
        self.DRAIN_HSV_V_LOW = int(config['V_LOW'])
        self.DRAIN_HSV_V_HIGH = int(config['V_HIGH'])

    def get_tank_image(self, image):
        self.color_image = image[self.y: self.y + self.h, self.x: self.x + self.w, :]
        return self.color_image

    def find(self, frame):

        cam_config = self.config['CAMERA']

        y_offset_start = int(
            int(cam_config['HEIGHT']) * float(cam_config['PRC_ROI_Y_START']) // 100)
        y_offset_end = int(
            int(cam_config['HEIGHT']) * float(cam_config['PRC_ROI_Y_END']) // 100)

        image = frame
        # image = frame.copy()
        image[:y_offset_start, :] = 255  # CONFIG TABLE OFFSET

        # image = cv.GaussianBlur(image, (7,7), 0)
        image = cv.blur(image, (9, 9), cv.BORDER_WRAP)
        # _, image = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        _, image = cv.threshold(image, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)  # Test

        mid_x = image.shape[1] // 2
        mid_y = image.shape[0] // 2

        # Search for the central line (in pink) and count the black pixel quantity
        x_center_offset = int(
            float(cam_config["PRC_CENTER_X_OFFSET"]) * int(cam_config['WIDTH']) // 100)
        vector_y = image[:, mid_x + x_center_offset]
        roi_vector_y = vector_y[y_offset_start:y_offset_end]
        roi_vector_y = roi_vector_y[roi_vector_y == 0]

        if roi_vector_y.size > int(self.MIN_HEIGHT):
            self.h = roi_vector_y.size
        else:
            self.h = 0
            self.found = False
            return False

        self.y = np.where(vector_y == 0)[0][0]  # Get the first black pixel

        center_y = (self.y + self.h) // 2
        off1 = int(float(cam_config['PRC_ROI_X_START'])
                   * int(cam_config['WIDTH']) // 100)
        off2 = int(float(cam_config['PRC_ROI_X_END'])
                   * int(cam_config['WIDTH']) // 100)

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

        # self.found = True if self.h >= self.MIN_HEIGHT else False
        self.found = self.h >= self.MIN_HEIGHT
        self.image = frame[self.y: self.y + self.h, self.x: self.x + self.w]

    def get_sticker_position_lab(self, frame):

        tank = frame[self.y: self.y + self.h, self.x: self.x + self.w]
        # blur ???
        kernel = np.ones((5,5), np.uint8) # GET the kernel from config
        lab = cv.cvtColor(tank, cv.COLOR_BGR2LAB)        
        low = np.array([self.STICKER_L_LOW,self.STICKER_A_LOW,self.STICKER_B_LOW])
        high = np.array([self.STICKER_L_HIGH, self.STICKER_A_HIGH,self.STICKER_B_HIGH])
        
        mask = cv.inRange(lab, low, high)         
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel, iterations=2)
        cnt, hier = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        if self.debug_sticker:            
            cv.imshow('debug_tank_sticker', mask)

        self.stickers = []
        for c in cnt:
            area = cv.contourArea(c)
            cond = area >= self.STICKER_MIN_AREA
            cond = cond and area <= self.STICKER_MAX_AREA
            if cond:                
                arc = cv.arcLength(c, True)
                poly = cv.approxPolyDP(c, arc * 0.02, True)
                if len(poly) == 4:                                        
                    (x, y, w, h) = cv.boundingRect(c)                    
                    ar = w / float(h)
                    cond = ar >= 0.92 and ar <= 1.08
                    cond = h >= self.STICKER_MIN_HEIGHT
                    cond = cond and h <= self.STICKER_MAX_HEIGHT
                    cond = cond and w >= self.STICKER_MIN_WIDTH
                    cond = cond and w <= self.STICKER_MAX_WIDTH
                    if cond:
                        sticker = Sticker(self.x + x, self.y + y, w, h)
                        sticker.area = area
                        sticker.image = tank[y:y+h, x:x+w]
                        zero_x = self.w // 2
                        zero_y = self.h // 2                        
                        sticker.relative_x = x - zero_x + (w // 2)
                        sticker.relative_y = (-1) * (y - zero_y) - (h // 2)
                        self.stickers.append(sticker)                                            

    def get_sticker_position(self, frame):

        threshold_min = 172  # param       
        tank = frame[self.y: self.y + self.h, self.x: self.x + self.w]

        blur = cv.blur(tank, (5, 5), cv.BORDER_CONSTANT) # Get kernel from config
        _, thresh = cv.threshold(blur, threshold_min, 255, cv.THRESH_BINARY)        

        # _, thres = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        cnt, hier = cv.findContours(thresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        if self.debug_sticker:
            cv.imshow('debug_tank_sticker')

        for c in cnt:
            area = cv.contourArea(c)
            cond = area >= STICKER.MIN_AREA and area <= STICKER.MAX_AREA           
            if cond:
                arc = cv.arcLength(c, True)
                poly = cv.approxPolyDP(c, arc * 0.02, True)
                if len(poly) == 4:                    
                    (x, y, w, h) = cv.boundingRect(c)
                    ar = w / float(h)
                    cond = ar >= 0.95 and ar <= 1.05
                    cond = h >= STICKER.MIN_HEIGHT
                    cond = cond and h <= STICKER.MAX_HEIGHT
                    cond = cond and w >= STICKER.MIN_WIDTH
                    cond = cond and w <= STICKER.MAX_WIDTH                  
                    if cond:                    
                        sticker = Sticker(self.x + x, self.y + y, w, h)
                        sticker.area = area
                        sticker.image = tank[y:y+h, x:x+w]
                        zero_x = self.w // 2
                        zero_y = self.h // 2                        
                        sticker.relative_x = x - zero_x + (w // 2)
                        sticker.relative_y = (-1) * (y - zero_y) - (h // 2)
                        self.stickers.append(sticker)   

    def get_drain(self, frame):

        cam_config = self.config['CAMERA']

        y_offset_start = int(
            int(cam_config['HEIGHT']) * float(cam_config['PRC_ROI_Y_START']) // 100)
        y_offset_end = int(
            int(cam_config['HEIGHT']) * float(cam_config['PRC_ROI_Y_END']) // 100)        

        crop_mask = np.ones(
            (int(cam_config['HEIGHT']), int(cam_config['WIDTH'])), np.uint8)

        # Corta as laterais
        crop_mask[:, 0:self.x + 10] = 0
        crop_mask[:, self.x + self.w - 10:] = 0

        # Eixo Y
        crop_mask[0: int(self.y - (self.h * 0.17)), :] = 0        

        # Cortar o centro mais % para cima e para baixo
        y_center = self.y + (self.h // 2)
        crop_mask[int(y_center - self.h * 0.4) : int(y_center + self.h * 0.34), :] = 0

        croped_img = cv.bitwise_and(frame, frame, mask=crop_mask)        

        hsv = cv.cvtColor(croped_img, cv.COLOR_BGR2HSV)      
        mask_low = self.DRAIN_FILTER_MASK_LOW
        mask_high = self.DRAIN_FILTER_MASK_HIGH

        blur_kernel = self.DRAIN_FILTER_BLUR

        blur = cv.GaussianBlur(hsv, blur_kernel, 1)
        mask = cv.inRange(blur, mask_low, mask_high)        

        kernel_open = np.ones(self.DRAIN_FILTER_OPEN, np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel_open, iterations=2)        

        if self.debug_drain:
            cv.imshow('debug_drain', mask)

        cnt, hier = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        self.drain_found = False
        self.drain_x, self.drain_y, self.drain_w, self.drain_h = 0, 0, 0, 0        

        for c in cnt:
            area = cv.contourArea(c)
            (x, y, w, h) = cv.boundingRect(c)
            cond = area >= self.DRAIN_AREA_MIN and area < self.DRAIN_AREA_MAX
            if cond:
                self.drain_found = True
                self.drain_x, self.drain_y, self.drain_w, self.drain_h = x, y, w, h

                zero_x = self.x + self.w // 2
                zero_y = self.y + self.h // 2                
                self.drain_rel_x = x - zero_x + (w // 2)                
                self.drain_rel_y = (-1) * (y - zero_y) - (h // 2)

                
    def get_drain_lab(self, frame, ):
        # TODO: Eliminar o berço
        cam_config = self.config['CAMERA']

        y_offset_start = int(
            int(cam_config['HEIGHT']) * float(cam_config['PRC_ROI_Y_START']) // 100)
        y_offset_end = int(
            int(cam_config['HEIGHT']) * float(cam_config['PRC_ROI_Y_END']) // 100)               

        crop_mask = np.ones(
            (int(cam_config['HEIGHT']), int(cam_config['WIDTH'])), np.uint8)

        # Laterais
        crop_mask[:, 0:self.x + 10] = 0
        crop_mask[:, self.x + self.w - 10:] = 0

        # Eixo Y
        # crop_mask[0: int(self.y - (self.h * 0.10)), :] = 0

        # Cortar o centro mais % para cima e para baixo
        y_center = self.y + (self.h // 2)
        crop_mask[int(y_center - self.h * 0.4) : int(y_center + self.h * 0.34), :] = 0

        croped_img = cv.bitwise_and(frame, frame, mask=crop_mask)
               
        lab = cv.cvtColor(croped_img, cv.COLOR_BGR2LAB) # LAB
        hsv = cv.cvtColor(croped_img, cv.COLOR_BGR2HSV) # HSV
        blur_kernel = self.DRAIN_FILTER_BLUR
        blur = cv.GaussianBlur(lab, blur_kernel, 1)

        # TEST WITH HSV FILTER ADD
        # hsv_low_mask = np.array([7, 20, 10]) # add in config
        # hsv_high_mask = np.array([25, 255, 255]) # add in config
        hsv_low_mask =  np.array([self.DRAIN_HSV_H_LOW,  self.DRAIN_HSV_S_LOW,  self.DRAIN_HSV_V_LOW])  # add in config
        hsv_high_mask = np.array([self.DRAIN_HSV_H_HIGH, self.DRAIN_HSV_S_HIGH, self.DRAIN_HSV_V_HIGH]) # add in config
        hsv_mask = cv.inRange(hsv, hsv_low_mask, hsv_high_mask)

        # --------------------------

        mask_low =  np.array([self.DRAIN_LAB_L_LOW, self.DRAIN_LAB_A_LOW, self.DRAIN_LAB_B_LOW], np.uint8)
        mask_high = np.array([self.DRAIN_LAB_L_HIGH, self.DRAIN_LAB_A_HIGH, self.DRAIN_LAB_B_HIGH], np.uint8)

        lab_mask = cv.inRange(blur, mask_low, mask_high)        

        # mask = lab_mask + hsv_mask -- Aditive
        # mask = cv.bitwise_and(lab_mask, hsv_mask)  # subtrative
        mask = lab_mask  # just lab

        kernel = np.ones(self.DRAIN_FILTER_KERNEL, np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel, iterations=2)
       
        if self.debug_drain:
            cv.imshow('debug_drain', mask)
            cv.imshow('debug_drain_lab', lab_mask)
            cv.imshow('debug_drain_hsv', hsv_mask)

        cnt, hier = cv.findContours(
            mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        self.drain_found = False
        self.drain_area = 0
        self.drain_x, self.drain_y, self.drain_w, self.drain_h = 0, 0, 0, 0

        sorted_cnts = sorted(cnt, key=lambda cnt: cv.contourArea(cnt))

        if len(sorted_cnts):
            c = sorted_cnts[-1]
            area = cv.contourArea(c)
            cond = area >= int(self.DRAIN_AREA_MIN) and area <= self.DRAIN_AREA_MAX 
            if cond:
                self.drain_found = True                
                (x, y, w, h) = cv.boundingRect(c)
                self.drain_x, self.drain_y, self.drain_w, self.drain_h = x, y, w, h
                self.drain_area = area
                zero_x = self.x + self.w // 2
                zero_y = self.y + self.h // 2                
                self.drain_rel_x = x - zero_x + (w // 2)
                self.drain_rel_y = (-1) * (y - zero_y) - (h // 2)                

        # for c in cnt:
        #     area = cv.contourArea(c)
        #     cond = area >= int(self.DRAIN_AREA_MIN) and area <= self.DRAIN_AREA_MAX 
        #     if cond:
        #         self.drain_found = True                
        #         (x, y, w, h) = cv.boundingRect(c)
        #         self.drain_x, self.drain_y, self.drain_w, self.drain_h = x, y, w, h
        #         self.drain_area = area
        #         zero_x = self.x + self.w // 2
        #         zero_y = self.y + self.h // 2                
        #         self.drain_rel_x = x - zero_x + (w // 2)
        #         self.drain_rel_y = (-1) * (y - zero_y) - (h // 2)
        #         # self.drain_rel_y = zero_y - y

   
        