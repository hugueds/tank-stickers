import argparse
import logging
import cv2 as cv
import platform
from time import sleep, time
from threading import Thread
from configparser import ConfigParser
from classes import Tank, Sticker, Camera, Model
from classes.image_writter import *
from classes.comands import *

system = platform.system()
date_fmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt=date_fmt)

config = ConfigParser()
config.read("test_config.ini")

camera = Camera(config["CAMERA"])
tank = Tank(config)
model = Model(config["MODEL"])

if system == "Windows":
    camera.start(cv.VideoCapture(cv.CAP_DSHOW))
else:
    camera.start(cv.VideoCapture(0))

enabled = True
tracker = False
orig = 0

def updateTracker(key, value):
    setattr(tank, key, value)

if __name__ == "__main__":

    logging.info("Starting Test Example")

    try:
        _, frame = camera.read()

        while enabled:

            last_time = time()

            if not camera.pause:
                success, frame = camera.read()
                if not success:
                    logging.error('Error during frame capture')
                    break
                orig = frame.copy()
                g_frame = cv.cvtColor(orig, cv.COLOR_BGR2GRAY)

            tank.get_sticker_position_lab(orig)  # Get the sticker from the image

            for sticker in tank.stickers:
                sticker.label_index, sticker.label = model.predict(sticker.image)
                sticker.update_position()

            draw_sticker(frame, tank)

            camera.update_frame_counter()
            camera.show(frame)

            key = cv.waitKey(10) & 0xFF
            key_pressed(key, camera, tank)

            if key == 27 or key == ord("q") or key == ord("Q"):
                enabled = False

            camera.fps = round(1 / (time() - last_time), 2)

        logging.info("Exiting Program")
        camera.cap.release()
        cv.destroyAllWindows()
        exit(0)

    except Exception as e:
        logging.exception(f"main::{str(e)}")
        camera.cap.release()
        cv.destroyAllWindows()
        exit(1)

