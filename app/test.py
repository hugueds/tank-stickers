from time import sleep
from classes import Camera, Controller, controller
from imutils.video.webcamvideostream import WebcamVideoStream
import cv2 as cv
from logger import logger


controller = Controller(True)

# controller.read_file('../test.jpg')

while True:
    controller.show_circle()
    controller.get_command()



