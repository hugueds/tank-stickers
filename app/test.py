from time import sleep
from classes import Camera, Controller
from imutils.video.webcamvideostream import WebcamVideoStream
import cv2 as cv


camera = Camera()

camera.start()

while True:    
    camera.show()
    
    
    