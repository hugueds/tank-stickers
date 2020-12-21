import numpy as np
import cv2 as cv

class Tracker():
    
    threshold_min = 127
    threshold_max = 255
    
    fps = 30    
    blur = 3
    erode = 1
    dilate = 1
    canny_min = 0
    canny_max = 255
    
    pause = 0

    def __init__(self, l_h, h_h, l_s, h_s, l_v, h_v):
        self.l_h = l_h
        self.h_h = h_h
        self.l_s = l_s
        self.h_s = h_s
        self.l_v = l_v
        self.h_v = h_v        

    
    def updateKernel(self, name, value):
        if value % 2 != 0:
            setattr(self, name, value)                        
    
    def update(self, name, value):        
        setattr(self, name, value)
    
    def getMask(self, image):
        
        low = np.array([self.l_h, self.l_s,  self.l_v], np.uint8)
        high = np.array([self.h_h, self.h_s,  self.h_v], np.uint8)     

        mask = cv.inRange(image, low, high)        
        
        if self.blur > 0:
            mask = cv.GaussianBlur(mask, (self.blur, self.blur), 0, cv.BORDER_CONSTANT)

        if self.dilate > 0:
            kernel_d = np.ones((self.dilate, self.dilate), np.uint8)
            mask = cv.dilate(mask, kernel_d, borderType=cv.BORDER_CONSTANT)

        if self.erode > 0:
            kernel_e = np.ones((self.erode, self.erode), np.uint8)
            mask = cv.erode(mask, kernel_e, borderType=cv.BORDER_CONSTANT)

        masked = cv.bitwise_and(image, image, mask=mask)   
        return mask, masked
    
    def save():
        pass
    
    def nothing(self):
        pass
