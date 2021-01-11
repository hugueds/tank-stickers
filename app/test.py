import os
from time import sleep

import cv2 as cv
from imutils.video.webcamvideostream import WebcamVideoStream

from classes import Camera, Controller, controller
from logger import logger

controller = Controller(is_picture=True)

path = "../images/drain"
folders = os.listdir(path)

file_list = []
index = 0

for folder in folders:
    files = os.listdir(f"{path}/{folder}")
    for file in files:
        file_list.append(f"{path}/{folder}/{file}")

controller.open_file(file_list[index])

while True:
    controller.get_frame()
    controller.process()
    controller.show()

    if cv.waitKey(10) & 0xFF == ord("*"):
        index += 1
        if index >= len(file_list):
            print("last_file reached")
            break
        controller.get_frame()
        frame = controller.file_frame.copy()
        frame = controller.tank.get_roi(frame)
        controller.open_file(file_list[index])
        cv.imwrite(file_list[index], frame)

    controller.get_command()
