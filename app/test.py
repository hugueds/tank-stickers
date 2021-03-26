import os
from time import sleep
import cv2 as cv
from classes import Controller
from logger import logger
import sys

controller = Controller(is_picture=True)

file = './tests/images/test_3.jpg'

if len(sys.argv) == 2:
    file = sys.argv[1]    

controller.open_file(file)

while True:
    controller.get_frame()
    controller.process()
    controller.show()
    controller.get_command()
