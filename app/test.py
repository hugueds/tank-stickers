from time import sleep
from classes import Camera, Controller, controller
from imutils.video.webcamvideostream import WebcamVideoStream
import cv2 as cv
from logger import logger
import os


controller = Controller(is_picture=True)
controller.start_plc()

path = '../images/drain'
folders = os.listdir(path)

for folder in folders:
    files = os.listdir(f'{path}/{folder}')
    for file in files:
        controller.open_file(f'{path}/{folder}/{file}')
        print(f'{path}/{folder}/{file}')
        # controller.get_frame(picture=True)
        controller.process()
        controller.show()
        # cv.waitKey(0)
        controller.get_command()

# # controller.open_file('../images/drain/10/SCREENSHOT_2021-01-05_094311.jpg')
# controller.open_file('./test.jpg')
# controller.start_plc()


# while True:
#     controller.get_frame(picture=True)
#     controller.process()
#     controller.show()
#     controller.get_command()
