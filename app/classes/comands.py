from classes.tank import Tank
from classes.camera import Camera
from models.camera_constants import CameraConstants
import logging
import cv2 as cv
from configparser import ConfigParser
from datetime import datetime

help_window = False
tracker_window = False
camera_tracker_window = False

def key_pressed(key, camera: Camera, tank: Tank):

    if key > 0 and chr(key) != "ÿ":
        logging.info('Key Pressed ' + chr(key))
    else:
        return

    if key == ord("h") or key == ord("H"):
        open_help()
    elif key == ord("p"):
        pause(camera)
    elif key == ord("+"):
        skip_frames(camera)
    elif key == ord("-"):
        rewind_frames(camera)
    elif key == ord("s"):
        save_image(camera)
    elif key == ord("v"):
        record(camera)
    elif key == ord("r"):
        reload_config(camera, tank)
    elif key == ord('1'):
        open_sticker_debug(tank)
    elif key == ord('2'):
        open_drain_debug(tank)
    elif key == ord("t"):
        open_tracker(camera, tank)
    elif key == ord("c"):
        open_camera_tracker(camera)


def disable():
    pass


def open_help():
    global help_window
    if not help_window:
        help_window = True
        img = cv.imread("help.png")
        cv.imshow("Instructions", img)
    else:
        help_window = False
        cv.destroyWindow("Instructions")


def save_image(camera: Camera, gray=False):
    _, frame = camera.read()
    now = datetime.now()
    str_date = now.strftime("%Y-%m-%d_%H%M%S")
    file_name = f"SCREENSHOT_{str_date}.jpg"
    path = "../captures/" + file_name
    cv.imwrite(path, frame)
    logging.info(f"Screenshot saved in " + path)


def record(camera: Camera):
    if not camera.recording:
        logging.info("START RECORDING...")
        camera.recording = True
        now = datetime.now()
        str_date = now.strftime("%Y-%m-%d_%H%M%S")
        file_name = f"RECORDING_{str_date}.avi"
        path = "../captures/" + file_name
        writter = cv.VideoWriter_fourcc("M", "J", "P", "G")
        camera.output = cv.VideoWriter(path, writter, 10, (1280, 720))
    else:
        logging.info("STOP RECORDING")
        camera.recording = False
        camera.output.release()


def close():
    pass


def skip_frames(camera: Camera):
    logging.info("Adding frames")
    current_frame = camera.cap.get(cv.CAP_PROP_POS_FRAMES)
    frame = current_frame + camera.SKIP_FRAMES
    camera.cap.set(cv.CAP_PROP_POS_FRAMES, frame)


def rewind_frames(camera: Camera):
    logging.info("Subtracting frames")
    current_frame = camera.cap.get(cv.CAP_PROP_POS_FRAMES)
    if current_frame > camera.SKIP_FRAMES:
        frame = current_frame - camera.SKIP_FRAMES
        camera.cap.set(cv.CAP_PROP_POS_FRAMES, frame)


def pause(camera: Camera):
    camera.pause = not camera.pause
    status = "Pause" if camera.pause else "Play"
    logging.info(status + " Video Stream")


def reload_config(camera: Camera, tank: Tank):
    logging.info("Reloading configuration")
    config = ConfigParser()
    config.read("config.ini")
    camera.load_config(config["CAMERA"])
    tank.load_config(config["TANK"])
    tank.load_sticker_config(config["STICKER"])
    tank.load_drain_config(config["DRAIN"])


def open_sticker_debug(tank: Tank):
    if tank.debug_sticker:
        cv.destroyWindow('debug_tank_sticker')
    tank.debug_sticker = not tank.debug_sticker


def open_drain_debug(tank: Tank):
    if tank.debug_drain:
        cv.destroyWindow('debug_drain')
        cv.destroyWindow('debug_drain_lab')
        cv.destroyWindow('debug_drain_hsv')
    tank.debug_drain = not tank.debug_drain


def updateTracker(obj, key, value):
    setattr(obj, key, value)

def update_camera_config(camera: Camera, key, value):
    setattr(camera, key, value)



def open_tracker(camera: Camera, tank: Tank):
    global tracker_window
    if not tracker_window:
        cv.namedWindow("config")
        cv.resizeWindow('config', 1200, 800)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        # cv.createTrackbar("hsv_drain_low_h", "config",  tank.DRAIN_HSV_H_LOW, 255, lambda value,  key='DRAIN_HSV_H_LOW': updateTracker(tank, key, value))
        # cv.createTrackbar("hsv_drain_high_h", "config", tank.DRAIN_HSV_H_HIGH, 255, lambda value, key='DRAIN_HSV_H_HIGH': updateTracker(tank, key, value))
        # cv.createTrackbar("hsv_drain_low_s", "config",  tank.DRAIN_HSV_S_LOW, 255, lambda value,  key='DRAIN_HSV_S_LOW': updateTracker(tank, key, value))
        # cv.createTrackbar("hsv_drain_high_s", "config", tank.DRAIN_HSV_S_HIGH, 255, lambda value, key='DRAIN_HSV_S_HIGH': updateTracker(tank, key, value))
        # cv.createTrackbar("hsv_drain_low_v", "config",  tank.DRAIN_HSV_V_LOW, 255, lambda value,  key='DRAIN_HSV_V_LOW': updateTracker(tank, key, value))
        # cv.createTrackbar("hsv_drain_high_v", "config", tank.DRAIN_HSV_V_HIGH, 255, lambda value, key='DRAIN_HSV_V_HIGH': updateTracker(tank, key, value))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        cv.createTrackbar("DRAIN_LL", "config", tank.drain_lab['low'][0], 255,  lambda value, key='DRAIN_LAB_L_LOW':  updateTracker(tank, key, value))
        cv.createTrackbar("DRAIN_HL", "config", tank.drain_lab['high'][0], 255, lambda value, key='DRAIN_LAB_L_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("DRAIN_LA", "config", tank.drain_lab['low'][1], 255,  lambda value, key='DRAIN_LAB_A_LOW':  updateTracker(tank, key, value))
        cv.createTrackbar("DRAIN_HA", "config", tank.drain_lab['high'][1], 255, lambda value, key='DRAIN_LAB_A_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("DRAIN_LB", "config", tank.drain_lab['low'][2], 255,  lambda value, key='DRAIN_LAB_B_LOW':  updateTracker(tank, key, value))
        cv.createTrackbar("DRAIN_HB", "config", tank.drain_lab['high'][2], 255, lambda value, key='DRAIN_LAB_B_HIGH': updateTracker(tank, key, value))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        # cv.createTrackbar("STICKER_LL",  "config",  tank.STICKER_L_LOW,  255, lambda value,  key='STICKER_L_LOW': updateTracker(tank, key, value))
        # cv.createTrackbar("STICKER_HL",  "config",  tank.STICKER_L_HIGH, 255, lambda value,  key='STICKER_L_HIGH': updateTracker(tank, key, value))
        # cv.createTrackbar("STICKER_LA",  "config",  tank.STICKER_A_LOW,  255, lambda value,  key='STICKER_A_LOW': updateTracker(tank, key, value))
        # cv.createTrackbar("STICKER_HA",  "config",  tank.STICKER_A_HIGH, 255, lambda value,  key='STICKER_A_HIGH': updateTracker(tank, key, value))
        # cv.createTrackbar("STICKER_LB",  "config",  tank.STICKER_B_LOW,  255, lambda value,  key='STICKER_B_LOW': updateTracker(tank, key, value))
        # cv.createTrackbar("STICKER_HB",  "config",  tank.STICKER_B_HIGH, 255, lambda value,  key='STICKER_B_HIGH': updateTracker(tank, key, value))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------

        cv.createTrackbar("cam_bright", "config", camera.brightness, 255, lambda value, key='brightness': update_camera_config(camera, key, value))
        # cv.createTrackbar("cam_sharpness", "config", camera.sharpness, 255, nothing)
        # cv.createTrackbar("cam_contrast", "config", 0, 255, nothing)
        # cv.createTrackbar("cam_saturation", "config", 0, 255, nothing)
    else:
        cv.destroyWindow('config')

    tracker_window = not tracker_window


def update_camera_config(camera, key, value):
    pass

def open_camera_tracker(camera):

    global camera_tracker_window

    BRIGHTNESS = 10
    CONTRAST = 11
    SATURATION = 12
    HUE = 13
    GAIN = 14
    EXPOSURE = 15
    WHITE_BALANCE = 17
    FOCUS = 28
    SHARPNESS = 0

    if not camera_tracker_window:
        cv.namedWindow("camera_tracker")
        cv.resizeWindow('camera_tracker', 640, 480)
        # camera.cap.set(BRIGHTNESS, 180) # min: 0 max: 255 increment:1
        # camera.cap.set(CONTRAST, 140) # min: 0 max: 255 increment:1
        # camera.cap.set(SATURATION, 255) # min: 0 max: 255 increment:1
        # camera.cap.set(HUE, 255) # hue
        # # camera.cap.set(GAIN, 62)  # min: 0 max: 127 increment:1
        # camera.cap.set(EXPOSURE, -6) # min: -7 max: -1 increment:1
        # camera.cap.set(WHITE_BALANCE, 4200) # min: 4000 max: 7000 increment:1
        # camera.cap.set(FOCUS, 0)  # focus          min: 0   , max: 255 , increment:5
        cv.createTrackbar("BRIGHTNESS", "camera_tracker",  180, 255, lambda value,  key='BRIGHTNESS':  updateTracker(camera, key, value))
        cv.createTrackbar("CONTRAST", "camera_tracker", 140, 255, lambda value, key='CONTRAST': updateTracker(camera, key, value))
        cv.createTrackbar("SATURATION", "camera_tracker",  255, 255, lambda value,  key='SATURATION':  updateTracker(camera, key, value))
        cv.createTrackbar("HUE", "camera_tracker", 127, 255, lambda value, key='HUE': updateTracker(camera, key, value))
        # cv.createTrackbar("EXPOSURE", "camera_tracker",  camera.DRAIN_HSV_V_LOW, 255, lambda value,  key='EXPOSURE':  updateTracker(camera, key, value))
        cv.createTrackbar("WHITE_BALANCE", "camera_tracker", 4200, 7000, lambda value, key='WHITE_BALANCE': updateTracker(camera, key, value))
        cv.createTrackbar("FOCUS", "camera_tracker", 0, 255, lambda value, key='FOCUS': updateTracker(camera, key, value))

    else:
        cv.destroyWindow('camera_tracker')

    camera_tracker_window = not camera_tracker_window


