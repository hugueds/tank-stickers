from time import sleep
from classes import Camera, Controller, controller
from imutils.video.webcamvideostream import WebcamVideoStream
import cv2 as cv
from logger import logger


controller = Controller()
# controller.open_file('../images/drain/10/SCREENSHOT_2021-01-05_094311.jpg')
controller.open_file('./test.jpg')
controller.start_plc()


while True:
    controller.get_frame(picture=True)
    controller.process()
    controller.show()
    controller.get_command()



