import os
from time import sleep
import cv2 as cv
from classes import Controller
from logger import logger

controller = Controller(is_picture=True)

controller.open_file('./tests/images/test_1.jpg')

while True:
    controller.get_frame()
    controller.process()
    controller.show()
    controller.get_command()
