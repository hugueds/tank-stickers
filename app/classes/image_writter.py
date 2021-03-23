from models.plc_write_interface import PLCWriteInterface
from models.plc_read_interface import PLCInterface
import cv2 as cv
import numpy as np
from classes import Camera, PLC, Tank
from classes.colors import *

font = cv.FONT_HERSHEY_SIMPLEX
offset = 25

def draw_roi_lines(frame: np.ndarray, camera: Camera) -> np.ndarray:
    color = cyan
    (y, x) = frame.shape[:2]
    x_start = int(camera.width * camera.roi['x'][0] // 100)
    x_end = int(camera.width * camera.roi['x'][1] // 100)
    y_start = int(camera.height * camera.roi['y'][0] // 100)
    y_end = int(camera.height * camera.roi['y'][1] // 100)

    cv.line(frame, (x_start, 0), (x_start, y), color, 1)
    cv.line(frame, (x_end, 0), (x_end, y), color, 1)
    cv.line(frame, (0, y_start), (x, y_start), color, 1)
    cv.line(frame, (0, y_end), (x, y_end), color, 1)
    return frame


def draw_center_axis(frame: np.ndarray, camera: Camera) -> np.ndarray:
    color = fucshia
    (y, x) = frame.shape[:2]
    x_offset = int(x // 2 + (camera.width * camera.center_x_offset) // 100)
    cv.line(frame, (x_offset, 0), (x_offset, y), color)

    y_offset = int(y // 2 + (camera.height * camera.center_y_offset) // 100)
    cv.line(frame, (0, y_offset), (x, y_offset), color)
    return frame

def draw_camera_info(frame: np.ndarray, camera: Camera) -> np.ndarray:
    text = f"Resolution {camera.width}x{camera.height} "
    color = navy_blue
    font_size = (frame.shape[1] * 0.0006)
    cv.putText(frame, text, (10, 15), font, font_size, color, 1)
    text = f"FPS: {camera.fps}, COUNTER: {camera.frame_counter}"
    cv.putText(frame, text, (10, 30), font, font_size, color, 1)
    if camera.recording:
        text = f" -- RECORDING --"
        color = red
        x, y = 0, 0  # use camera percentage
        cv.putText(frame, text, (500, 650), font, 0.7, color, 2)
    return frame


def draw_tank_center_axis(frame: np.ndarray, tank: Tank) -> np.ndarray:
    x, y, w, h = tank.x, tank.y, tank.w, tank.h
    cv.line(frame, (x, y + (h // 2)), (x + w, y + (h // 2)), red, 1)
    cv.line(frame, (x + (w // 2), y), (x + (w // 2), y + h), red, 1)
    return frame


def draw_tank_rectangle(frame: np.ndarray, tank: Tank) -> np.ndarray:
    color = tank_color
    x, y, w, h = tank.x, tank.y, tank.w, tank.h
    text = f"TANK X: {x}, Y: {y} - W: {w}, H: {h}"
    font_size = (frame.shape[1] * 0.0007)
    cv.putText(frame, text, (10, 45), font, font_size, tank_color, 1)
    cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    return frame


def draw_tank_circle(frame: np.ndarray, tank: Tank) -> np.ndarray:
    if tank.circles is not None:
        circles = np.uint16(np.around(tank.circles))
        for x, y, r in circles[0, :]:
            cv.circle(frame, (x, y), r, (0, 255, 0), 2)
            cv.line(frame, (x, y - r), (x, y + r), (0, 0, 255), 1)
            cv.line(frame, (x-r, y), (x+r, y), (0, 0, 255), 1)
    return frame

def draw_sticker(frame: np.ndarray, camera: Camera, tank: Tank) -> np.ndarray:
    i = 1
    for s in tank.stickers:
        color = color_list[s.label_index]
        text = f"STICKER [{s.label}] X {s.x} Y: {s.y}  "
        text += f"R_X {s.relative_x} R_Y {s.relative_y}  "
        text += f"AREA: {s.area} W: {s.w} H: {s.h} "
        text += f"Q: {s.quadrant} "
        cv.rectangle(frame, (s.x, s.y), (s.x + s.w, s.y + s.h), color, 2)
        font_size = (0.0006 * frame.shape[1])
        x = 10
        y = camera.height - (20 * i)
        cv.putText(frame, text, (x, y), font, font_size, color, 1)
        i += 1
    return frame

def draw_drain(frame: np.ndarray, tank: Tank) -> np.ndarray:
    if not tank.drain_found:
        return frame
    x, y = frame.shape[1], frame.shape[0]
    color = dark_yellow
    dx, dy, dw, dh = tank.drain_x, tank.drain_y, tank.drain_w, tank.drain_h
    cv.rectangle(frame, (dx, dy), (dx+dw, dy+dh), dark_yellow, 2)
    point = (10, 60)
    font_size = (0.0007 * x)
    text = f"DRAIN X: {tank.drain_rel_x} Y: {tank.drain_rel_y}, A: {tank.drain_area_found}, Q: {tank.drain_position}"
    cv.putText(frame, text, point, font, font_size, color, 2)
    return frame

def draw_drain_ml(frame: np.ndarray, tank: Tank) -> np.ndarray:
    if tank.drain_position == 0:
        return frame
    color = dark_yellow
    point = (10, 65)
    font_size = (0.00075 * frame.shape[1])
    text = f"DRAIN POSITION: {tank.drain_position}"
    cv.putText(frame, text, point, font, font_size, color, 2)
    return frame

def draw_plc_status(frame: np.ndarray, plc: PLC, read_plc: PLCInterface, write_plc: PLCWriteInterface) -> np.ndarray:
    x, y = frame.shape[1], frame.shape[0]
    start = int(0.73 * x)
    color = yellow
    font_size = (0.00055 * x)
    o = 14
    cv.rectangle(frame, (start, 0),(x, int(y * 0.25)), (30,30,30), -1)
    text = f"PLC ONLINE {plc.online}, LIFEBIT: {read_plc.life_beat}"
    cv.putText(frame, text, (start, 1 * o), font, font_size, color, 1)
    text = f"SKID #: {read_plc.skid}"
    cv.putText(frame, text, (start, 2 * o), font, font_size, color, 1)
    if write_plc.job_status == 1:
        text = f"CAM STS: {write_plc.cam_status} - JOB STS: {write_plc.job_status}"
        cv.putText(frame, text, (start, 3 * o), font, font_size, color, 1)
        text = f"POPID {read_plc.popid}, TANK: {read_plc.partnumber}"
        cv.putText(frame, text, (start, 4 * o), font, font_size, color, 1)
        text = f"PLC DRAIN POSITION: {read_plc.drain_position}"
        cv.putText(frame, text, (start, 5 * o), font, font_size, color, 1)
        text = f"PLC STICKER: {read_plc.sticker}"
        cv.putText(frame, text, (start, 6 * o), font, font_size, color, 1)
        text = f"PLC STICKER POSITION: {read_plc.sticker_position}"
        cv.putText(frame, text, (start, 7 * o), font, font_size, color, 1)
        text = f"PLC STICKER ANGLE: {read_plc.sticker_angle}"
        cv.putText(frame, text, (start, 8 * o), font, font_size, color, 1)
    return frame


def draw_gradient(frame: np.ndarray) -> np.ndarray:
    _, frame = cv.threshold(frame, 127, 255, cv.THRESH_BINARY)
    blur = cv.GaussianBlur(frame, (5, 5), 0)
    blur = cv.bilateralFilter(frame, 9, 75, 75)
    laplacian = cv.Laplacian(blur, cv.CV_64F)
    cv.imshow("Laplace", laplacian)
    return frame


def draw_sobel(frame: np.ndarray) -> np.ndarray:
    _, frame = cv.threshold(frame, 100, 255, cv.THRESH_BINARY)
    blur = cv.GaussianBlur(frame, (3, 3), 0)
    sobelx = cv.Sobel(blur, cv.CV_64F, 0, 1, ksize=3)
    sobely = cv.Sobel(blur, cv.CV_64F, 1, 0, ksize=3)
    cv.imshow("sobel", sobelx)
    return frame


def draw_canny(frame: np.ndarray) -> np.ndarray:
    _, frame = cv.threshold(frame, 50, 255, cv.THRESH_BINARY)
    sigma = 0.5
    v = np.median(frame)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    canny = cv.Canny(frame, lower, upper)
    cv.imshow("Canny", canny)
    cv.imshow("t", frame)
    return frame
