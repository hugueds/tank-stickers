from time import sleep
from classes import Camera, Controller, controller
from imutils.video.webcamvideostream import WebcamVideoStream
import cv2 as cv
from logger import logger


controller = Controller()

while True:
    controller.get_frame()
    controller.show_circle()
    controller.get_command()



