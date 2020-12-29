import argparse
import logging
import cv2 as cv
import platform
from time import sleep, time
from threading import Thread
from configparser import ConfigParser
from classes import Tank, Sticker, Camera, PLC, TFModel
from classes.image_writter import *
from classes.commands import *

system = platform.system()
date_fmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt=date_fmt)

parser = argparse.ArgumentParser()

parser.add_argument("--video", help="enable test a video")
parser.add_argument("--image", help="enable test an image")
parser.add_argument("--no-plc", action="store_true", help="run without PLC connection")
args = parser.parse_args()

camera = Camera()
tank = Tank()
plc = PLC()
model = TFModel()

if args.video:
    path = args.video
    camera.start()
    plc.enabled = False
elif args.image:
    path = args.image
    img = cv.imread(path, -1)
    camera.start()
    plc.enabled = False
else:
    if system == "Windows":
        camera.start()
    else:
        camera.start()

if args.no_plc:
    plc.enabled = False

enabled = True
tracker = False
orig = 0
g_frame = 0
img = 0

def updateTracker(key, value):
    setattr(tank, key, value)

def plc_thread():
    global plc, tank
    counter = 0
    logging.info("Starting PLC Thread")
    plc.connect()
    while True:
        try:
            if tank.found:
                pass
                # plc.write(tank)
            else:
                plc.clean_values()
            if counter % 50 == 0:
                plc.check_connection()
                counter = 0
            counter += 1
            sleep(plc.cycle)
        except Exception as e:
            logging.error(f"plc_thread::{e}")

if __name__ == "__main__":

    logging.info("Starting Poka Yoke - Tank Labels")

    if plc.enabled:
        plcThread = Thread(name="plc_thread", target=plc_thread, daemon=True)
        plcThread.start()

    try:
        _, frame = camera.read()

        while enabled:
            last_time = time()

            # Get the image, make a copy and get the HSV IMG
            if not camera.pause:
                success, frame = camera.read()
                if not success:
                    logging.error('Error during frame capture')
                    break
                if args.image:
                    frame = img
                orig = frame.copy()
                g_frame = cv.cvtColor(orig, cv.COLOR_BGR2GRAY)

            draw_center_axis(frame, camera)
            draw_roi_lines(frame, camera)

            tank.find(orig) # Get the Tank image and return if it was found

            if tank.found:
                draw_tank_center_axis(frame, tank)
                draw_tank_rectangle(frame, tank)
                # tank.get_drain(orig, config["CAMERA"]) # HSV - OLD
                tank.get_drain_lab(orig) # Get the drain position

                if tank.drain_found:
                    draw_drain(frame, tank)

                # tank.get_sticker_position(g_frame, sticker) # HSV - OLD
                tank.get_sticker_position_lab(orig)  # Get the sticker from the image
                for sticker in tank.stickers:
                    sticker.label_index, sticker.label = model.predict(sticker.image)
                    sticker.update_position()

                draw_sticker(frame, camera, tank)

            draw_camera_info(frame, camera)
            # draw_plc_status(frame, camera, plc)

            if camera.recording:
                camera.output.write(cv.resize(orig, (1280, 720)))
                # camera.output.write(cv.resize(frame, (1280, 720)))

            camera.update_frame_counter()
            camera.show(frame)

            # -----------------  Commands -------------------

            key = cv.waitKey(10) & 0xFF
            key_pressed(key, camera, tank)

            if key == 27 or key == ord("q") or key == ord("Q"):
                enabled = 0

            if args.video:
                camera.current_frame = camera.cap.get(cv.CAP_PROP_POS_FRAMES)
                sleep(1 / camera.fps)  # LIMIT ONLY IN RECORDED
            else:
                camera.fps = round(1 / (time() - last_time), 2)

        logging.info("Exiting Program")
        plc.disconnect()
        camera.stop()
        cv.destroyAllWindows()
        exit(0)

    except Exception as e:
        logging.exception(f"main::{str(e)}")
        plc.disconnect()
        camera.stop()
        cv.destroyAllWindows()
        exit(1)

