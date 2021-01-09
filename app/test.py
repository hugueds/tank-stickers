from time import sleep
from classes import Camera, Controller, controller
from imutils.video.webcamvideostream import WebcamVideoStream
import cv2 as cv
from logger import logger
import os


controller = Controller(is_picture=True)

path = '../images/drain'
folders = os.listdir(path)

file_list = []
index = 0

for folder in folders:
    files = os.listdir(f'{path}/{folder}')
    for file in files:
        file_list.append(f'{path}/{folder}/{file}')

controller.open_file(file_list[index])

while True:
    controller.get_frame(picture=True)
    controller.process()
    controller.show()
    if cv.waitKey(10) & 0xFF == ord('*'):
        index += 1
        if index >= len(file_list):
            print('last_file reached')
            break
        frame = controller.frame
        
        cv.imwrite(file_list[index], )
        controller.open_file(file_list[index])

    controller.get_command()
