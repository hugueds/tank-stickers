import logging
import cv2 as cv
from configparser import ConfigParser
from datetime import datetime

help_window = False
tracker_window = False


def key_pressed(key, camera, tank):

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


def save_image(camera, gray=False):
    _, frame = camera.read()
    now = datetime.now()
    str_date = now.strftime("%Y-%m-%d_%H%M%S")
    file_name = f"SCREENSHOT_{str_date}.jpg"
    path = "../captures/" + file_name
    cv.imwrite(path, frame)
    logging.info(f"Screenshot saved in " + path)


def record(camera):
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


def skip_frames(camera):
    logging.info("Adding frames")
    current_frame = camera.cap.get(cv.CAP_PROP_POS_FRAMES)
    frame = current_frame + camera.SKIP_FRAMES
    camera.cap.set(cv.CAP_PROP_POS_FRAMES, frame)


def rewind_frames(camera):
    logging.info("Subtracting frames")
    current_frame = camera.cap.get(cv.CAP_PROP_POS_FRAMES)
    if current_frame > camera.SKIP_FRAMES:
        frame = current_frame - camera.SKIP_FRAMES
        camera.cap.set(cv.CAP_PROP_POS_FRAMES, frame)


def pause(camera):
    camera.pause = not camera.pause
    status = "Pause" if camera.pause else "Play"
    logging.info(status + " Video Stream")


def reload_config(camera, tank):
    logging.info("Reloading configuration")
    config = ConfigParser()
    config.read("config.ini")
    camera.load_config(config["CAMERA"])
    tank.load_config(config["TANK"])
    tank.load_sticker_config(config["STICKER"])
    tank.load_drain_config(config["DRAIN"])


def open_sticker_debug(tank):
    if tank.debug_sticker:
        cv.destroyWindow('debug_tank_sticker')
    tank.debug_sticker = not tank.debug_sticker


def open_drain_debug(tank):
    if tank.debug_drain:
        cv.destroyWindow('debug_drain')
        cv.destroyWindow('debug_drain_lab')
        cv.destroyWindow('debug_drain_hsv')
    tank.debug_drain = not tank.debug_drain


def updateTracker(obj, key, value):
    setattr(obj, key, value)


def open_tracker(camera, tank):
    global tracker_window
    if not tracker_window:
        cv.namedWindow("config")
        cv.resizeWindow('config', 1200, 800)
        
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        cv.createTrackbar("hsv_drain_low_h", "config",  tank.DRAIN_HSV_H_LOW, 255, lambda value,  key='DRAIN_HSV_H_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("hsv_drain_high_h", "config", tank.DRAIN_HSV_H_HIGH, 255, lambda value, key='DRAIN_HSV_H_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("hsv_drain_low_s", "config",  tank.DRAIN_HSV_S_LOW, 255, lambda value,  key='DRAIN_HSV_S_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("hsv_drain_high_s", "config", tank.DRAIN_HSV_S_HIGH, 255, lambda value, key='DRAIN_HSV_S_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("hsv_drain_low_v", "config",  tank.DRAIN_HSV_V_LOW, 255, lambda value,  key='DRAIN_HSV_V_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("hsv_drain_high_v", "config", tank.DRAIN_HSV_V_HIGH, 255, lambda value, key='DRAIN_HSV_V_HIGH': updateTracker(tank, key, value))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        cv.createTrackbar("lab_drain_low_l", "config", tank.DRAIN_LAB_L_LOW, 255, lambda value, key='DRAIN_LAB_L_LOW': updateTracker(tank, key, value))                  
        cv.createTrackbar("lab_drain_high_l", "config", tank.DRAIN_LAB_L_HIGH, 255, lambda value, key='DRAIN_LAB_L_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("lab_drain_low_a", "config", tank.DRAIN_LAB_A_LOW, 255, lambda value, key='DRAIN_LAB_A_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("lab_drain_high_a", "config", tank.DRAIN_LAB_A_HIGH, 255, lambda value, key='DRAIN_LAB_A_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("lab_drain_low_b", "config", tank.DRAIN_LAB_B_LOW, 255, lambda value, key='DRAIN_LAB_B_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("lab_drain_high_b", "config", tank.DRAIN_LAB_B_HIGH, 255, lambda value, key='DRAIN_LAB_B_HIGH': updateTracker(tank, key, value))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------                         
        cv.createTrackbar("lab_sticker_low_l", "config",  tank.STICKER_L_LOW, 255, lambda value,  key='STICKER_L_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("lab_sticker_high_l", "config", tank.STICKER_L_HIGH, 255, lambda value, key='STICKER_L_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("lab_sticker_low_a", "config",  tank.STICKER_A_LOW, 255, lambda value,  key='STICKER_A_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("lab_sticker_high_a", "config", tank.STICKER_A_HIGH, 255, lambda value, key='STICKER_A_HIGH': updateTracker(tank, key, value))
        cv.createTrackbar("lab_sticker_low_b", "config",  tank.STICKER_B_LOW, 255, lambda value,  key='STICKER_B_LOW': updateTracker(tank, key, value))
        cv.createTrackbar("lab_sticker_high_b", "config", tank.STICKER_B_HIGH, 255, lambda value, key='STICKER_B_HIGH': updateTracker(tank, key, value))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------

        # cv.createTrackbar("cam_bright", "config", 0, 255, nothing)
        # cv.createTrackbar("cam_hue", "config", 0, 255, nothing)
        # cv.createTrackbar("cam_contrast", "config", 0, 255, nothing)
        # cv.createTrackbar("cam_saturation", "config", 0, 255, nothing)
    else:
        cv.destroyWindow('config')
    tracker_window = not tracker_window
