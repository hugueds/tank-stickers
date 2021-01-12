from models.plc_read_interface import PLCInterface
import cv2 as cv
import yaml
from datetime import datetime
from classes.tank import Tank
from classes.camera import Camera
from models.camera_constants import CameraConstants
from configparser import ConfigParser
from logger import logger

help_window = False
tracker_window = False
camera_tracker_window = False
full_screen = True

# TODO:
# REDUCE WINDOW
# COMANDS TO PLC

def key_pressed(key, camera: Camera, tank: Tank):

    if key > 0 and chr(key) != "ÿ":
        logger.info('Key Pressed ' + chr(key))
    else:
        return

    if key == ord("h") or key == ord("H"):
        pass
        # open_help()
    elif key == ord('q'):
        quit(0)
    elif key == ord("p"):
        pause(camera)
    elif key == ord("+"):
        skip_frames(camera)
    elif key == ord("-"):
        rewind_frames(camera)
    elif key == ord("s"):
        save_image(camera)
    elif key == ord("S"):
        save_image(camera, roi=True)
    elif key == ord("v"):
        record(camera)
    elif key == ord("r"):
        reload_config(camera, tank)
    elif key == ord('1'):
        open_sticker_debug(tank)
    elif key == ord('2'):
        open_drain_debug(tank)
    elif key == ord('3'):
        open_tank_debug(tank)
    elif key == ord("t"):
        open_tracker(camera, tank)
    elif key == ord("c"):
        open_camera_tracker(camera)
    elif key == ord('f'):
        set_full_screen(camera)


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


def save_image(camera: Camera, roi = False, gray=False):
    _, frame = camera.read()
    now = datetime.now()
    str_date = now.strftime("%Y-%m-%d_%H%M%S")
    file_name = f"SCREENSHOT_{str_date}.jpg"
    path = "../captures/" + file_name
    if roi:
        c_width, c_height = camera.width, camera.height
        roi = camera.roi
        y_off_start = int(c_height * roi["y"][0] // 100)
        y_off_end = int(c_height * roi["y"][1] // 100)
        x_off_start = int(roi["x"][0] * c_width // 100)
        x_off_end = int(roi["x"][1] * c_width // 100)
        frame = frame[y_off_start:y_off_end, x_off_start:x_off_end]
    cv.imwrite(path, frame)
    logger.info(f"Screenshot saved in " + path)


def record(camera: Camera):
    if not camera.recording:
        logger.info("START RECORDING...")
        camera.recording = True
        now = datetime.now()
        str_date = now.strftime("%Y-%m-%d_%H%M%S")
        file_name = f"RECORDING_{str_date}.avi"
        path = "../captures/" + file_name
        writter = cv.VideoWriter_fourcc("M", "J", "P", "G")
        camera.output = cv.VideoWriter(path, writter, 10, (640, 480))
    else:
        logger.info("STOP RECORDING")
        camera.recording = False
        camera.output.release()


def skip_frames(camera: Camera):
    logger.info("Adding frames")
    current_frame = camera.cap.get(cv.CAP_PROP_POS_FRAMES)
    frame = current_frame + camera.SKIP_FRAMES
    camera.cap.set(cv.CAP_PROP_POS_FRAMES, frame)


def rewind_frames(camera: Camera):
    logger.info("Subtracting frames")
    current_frame = camera.cap.get(cv.CAP_PROP_POS_FRAMES)
    if current_frame > camera.SKIP_FRAMES:
        frame = current_frame - camera.SKIP_FRAMES
        camera.cap.set(cv.CAP_PROP_POS_FRAMES, frame)

def pause(camera: Camera):
    camera.pause = not camera.pause
    status = "Pause" if camera.pause else "Play"
    logger.info(status + " Video Stream")

def reload_config(camera: Camera, tank: Tank):
    logger.info("Reloading configuration...")
    tank.load_config()
    camera.load_config()

def open_sticker_debug(tank: Tank):
    if tank.debug_sticker:
        cv.destroyWindow('debug_tank_sticker')
    tank.debug_sticker = not tank.debug_sticker

def open_tank_debug(tank: Tank):
    if tank.debug_tank:
        cv.destroyWindow('debug_tank')
    tank.debug_tank = not tank.debug_tank

def open_drain_debug(tank: Tank):
    if tank.debug_drain:
        cv.destroyWindow('debug_drain')
        cv.destroyWindow('debug_drain_lab')
        cv.destroyWindow('debug_drain_hsv')
    tank.debug_drain = not tank.debug_drain


def __updateTracker(obj, key, value, index):
    _filter = getattr(obj, key)
    if len(index) == 2:
        _filter[index[0]][index[1]] = value
    else:
        _filter[index[0]] = value
    setattr(obj, key, _filter)

def open_tracker(camera: Camera, tank: Tank):
    global tracker_window
    if not tracker_window:
        cv.namedWindow("config")
        cv.resizeWindow('config', 1200, 800)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        cv.createTrackbar("STICKER_LL", "config", tank.sticker_lab[0][0], 255, lambda value, key='sticker_lab', index=(0,0): __updateTracker(tank, key, value, index))
        cv.createTrackbar("STICKER_HL", "config", tank.sticker_lab[1][0], 255, lambda value, key='sticker_lab', index=(1,0): __updateTracker(tank, key, value, index))
        cv.createTrackbar("STICKER_LA", "config", tank.sticker_lab[0][1], 255, lambda value, key='sticker_lab', index=(0,1): __updateTracker(tank, key, value, index))
        cv.createTrackbar("STICKER_HA", "config", tank.sticker_lab[1][1], 255, lambda value, key='sticker_lab', index=(1,1): __updateTracker(tank, key, value, index))
        cv.createTrackbar("STICKER_LB", "config", tank.sticker_lab[0][2], 255, lambda value, key='sticker_lab', index=(0,2): __updateTracker(tank, key, value, index))
        cv.createTrackbar("STICKER_HB", "config", tank.sticker_lab[1][2], 255, lambda value, key='sticker_lab', index=(1,2): __updateTracker(tank, key, value, index))

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        cv.createTrackbar("C_PARAM1", "config", tank.params[0], 255,  lambda value, key='params', index=(0,):  __updateTracker(tank, key, value, index))
        cv.createTrackbar("C_PARAM2", "config", tank.params[1], 255,  lambda value, key='params', index=(1,):  __updateTracker(tank, key, value, index))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------

        # cv.createTrackbar("DRAIN_LL", "config", tank.drain_lab[0][0], 255,  lambda value, key='drain_lab', index=(0,0):  __updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_HL", "config", tank.drain_lab[1][0], 255,  lambda value, key='drain_lab', index=(1,0):  __updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_LA", "config", tank.drain_lab[0][1], 255,  lambda value, key='drain_lab', index=(0,1):  __updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_HA", "config", tank.drain_lab[1][1], 255,  lambda value, key='drain_lab', index=(1,1):  __updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_LB", "config", tank.drain_lab[0][2], 255,  lambda value, key='drain_lab', index=(0,2):  __updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_HB", "config", tank.drain_lab[1][2], 255,  lambda value, key='drain_lab', index=(1,2):  __updateTracker(tank, key, value, index))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        # cv.createTrackbar("DRAIN_LH", "config", tank.drain_hsv[0][0], 255,  lambda value, key='drain_hsv', index=(0,0):  updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_HH", "config", tank.drain_hsv[1][0], 255,  lambda value, key='drain_hsv', index=(1,0):  updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_LS", "config", tank.drain_hsv[0][1], 255,  lambda value, key='drain_hsv', index=(0,1):  updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_HS", "config", tank.drain_hsv[1][1], 255,  lambda value, key='drain_hsv', index=(1,1):  updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_LV", "config", tank.drain_hsv[0][2], 255,  lambda value, key='drain_hsv', index=(0,2):  updateTracker(tank, key, value, index))
        # cv.createTrackbar("DRAIN_HV", "config", tank.drain_hsv[1][2], 255,  lambda value, key='drain_hsv', index=(1,2):  updateTracker(tank, key, value, index))
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
        cv.createTrackbar("TABLE_LH", "config", tank.table_hsv[0][0], 255,  lambda value, key='table_hsv', index=(0,0):  __updateTracker(tank, key, value, index))
        cv.createTrackbar("TABLE_HH", "config", tank.table_hsv[1][0], 255,  lambda value, key='table_hsv', index=(1,0):  __updateTracker(tank, key, value, index))
        cv.createTrackbar("TABLE_LS", "config", tank.table_hsv[0][1], 255,  lambda value, key='table_hsv', index=(0,1):  __updateTracker(tank, key, value, index))
        cv.createTrackbar("TABLE_HS", "config", tank.table_hsv[1][1], 255,  lambda value, key='table_hsv', index=(1,1):  __updateTracker(tank, key, value, index))
        cv.createTrackbar("TABLE_LV", "config", tank.table_hsv[0][2], 255,  lambda value, key='table_hsv', index=(0,2):  __updateTracker(tank, key, value, index))
        cv.createTrackbar("TABLE_HV", "config", tank.table_hsv[1][2], 255,  lambda value, key='table_hsv', index=(1,2):  __updateTracker(tank, key, value, index))

    else:
        cv.destroyWindow('config')

    tracker_window = not tracker_window


def update_camera_config(camera: Camera, key, value):
    setattr(camera, key, value)
    if camera.rpi_camera:
        camera.set_hardware_rpi()
    else:
        camera.set_hardware_threaded()

def open_camera_tracker(camera: Camera):

    global camera_tracker_window

    if not camera_tracker_window:
        cv.namedWindow("camera_tracker")
        cv.resizeWindow('camera_tracker', 640, 480)
        cv.createTrackbar("BRIGHTNESS", "camera_tracker",  camera.brightness, 255, lambda value, key='brightness':  update_camera_config(camera, key, value))
        cv.createTrackbar("CONTRAST",   "camera_tracker",  camera.contrast,   255, lambda value, key='contrast':    update_camera_config(camera, key, value))
        cv.createTrackbar("SATURATION", "camera_tracker",  camera.saturation, 255, lambda value,  key='saturation':  update_camera_config(camera, key, value))
        cv.createTrackbar("SHARPNESS", "camera_tracker",  camera.sharpness, 255, lambda value,  key='sharpness':  update_camera_config(camera, key, value))
        cv.createTrackbar("EXPOSURE", "camera_tracker",    camera.exposure_comp, 255, lambda value,  key='exposure_comp':  update_camera_config(camera, key, value))
    else:
        cv.destroyWindow('camera_tracker')

    camera_tracker_window = not camera_tracker_window


def set_full_screen(camera: Camera):
    global full_screen
    full_screen = not full_screen
    if full_screen:
        cv.setWindowProperty(camera.window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    else:
        cv.resizeWindow(camera.window_name, camera.monitor_display)

