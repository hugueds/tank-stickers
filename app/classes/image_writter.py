from models.plc_write_interface import PLCWriteInterface
from models.plc_read_interface import PLCInterface
import cv2 as cv
import numpy as np
from classes import Camera, PLC, Tank
from classes.colors import *

font = cv.FONT_HERSHEY_SIMPLEX
offset = 25


def draw_roi_lines(frame: np.ndarray, camera: Camera):
    color = cyan
    (y, x) = frame.shape[:2]
    x_start = int(camera.width * camera.roi['x'][0] // 100)
    x_end = int(camera.width * camera.roi['x'][1] // 100)
    y_start = int(camera.height * camera.roi['y'][0] // 100)
    y_end = int(camera.height * camera.roi['y'][1] // 100)

    cv.line(frame, (x_start, 0), (x_start, y), color, 2)
    cv.line(frame, (x_end, 0), (x_end, y), color, 2)
    cv.line(frame, (0, y_start), (x, y_start), color, 2)
    cv.line(frame, (0, y_end), (x, y_end), color, 2)
    return frame


def draw_center_axis(frame: np.ndarray, camera: Camera):
    color = fucshia
    (y, x) = frame.shape[:2]
    x_offset = int(x // 2 + (camera.width * camera.center_x_offset) // 100)
    cv.line(frame, (x_offset, 0), (x_offset, y), color)
    cv.line(frame, (0, y // 2), (x, y // 2), color)
    return frame


def draw_camera_info(frame: np.ndarray, camera: Camera):
    text = f"Resolution {camera.width}x{camera.height} "
    color = navy_blue
    font_size = (frame.shape[1] * 0.0007)
    cv.putText(frame, text, (10, 25), font, font_size, color, 2)
    text = f"FPS: {camera.fps}, COUNTER: {camera.frame_counter}"
    cv.putText(frame, text, (10, 50), font, font_size, color, 2)
    if camera.recording:
        text = f" -- RECORDING --"
        color = red
        x, y = 0, 0  # use camera percentage
        cv.putText(frame, text, (500, 650), font, 0.7, color, 2)
    return frame


def draw_job_info(self):
    # display POPID, Parameter, Quadrant, LT, Sticker Label, Angle
    # display POPID, Parameter, Quadrant, LT, Sticker Label, Angle
    pass


def draw_tank_center_axis(frame: np.ndarray, tank: Tank):
    x, y, w, h = tank.x, tank.y, tank.w, tank.h
    cv.line(frame, (x, y + (h // 2)), (x + w, y + (h // 2)), red, 1)
    cv.line(frame, (x + (w // 2), y), (x + (w // 2), y + h), red, 1)
    return frame


def draw_tank_rectangle(frame: np.ndarray, tank: Tank):
    color = tank_color
    x, y, w, h = tank.x, tank.y, tank.w, tank.h
    text = f"TANK WIDTH {w}, HEIGHT {h}"
    # x,y = 0,0
    font_size = (frame.shape[1] * 0.0007)
    cv.putText(frame, text, (10, 75), font, font_size, tank_color, 2)
    cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    return frame


def draw_tank_circle(frame: np.ndarray, tank: Tank):
    if tank.circles is not None:
        circles = np.uint16(np.around(tank.circles))
        for x, y, r in circles[0, :]:
            cv.circle(frame, (x, y), r, (0, 255, 0), 2)
            cv.line(frame, (x, y - r), (x, y + r), (0, 0, 255), 1)
            cv.line(frame, (x-r, y), (x+r, y), (0, 0, 255), 1)
    return frame


def draw_drain(frame: np.ndarray, tank: Tank):
    x, y = frame.shape[1], frame.shape[0]
    color = dark_yellow
    dx, dy, dw, dh = tank.drain_x, tank.drain_y, tank.drain_w, tank.drain_h
    cv.rectangle(frame, (dx, dy), (dx+dw, dy+dh), dark_yellow, 2)
    point = (10, 100)
    font_size = (0.0007 * x)
    text = f"DRAIN X: {tank.drain_rel_x} Y: {tank.drain_rel_y}, AREA: {tank.drain_area_found}"
    cv.putText(frame, text, point, font, font_size, color, 2)
    return frame


def draw_plc_status(frame: np.ndarray, plc: PLC, read_plc: PLCInterface, write_plc: PLCWriteInterface):
    x, y = frame.shape[1], frame.shape[0]
    start = int(0.5, x)
    color = mid_blue
    font_size = (0.0007 * x)
    o = 25

    text = f"PLC STATUS {plc.online}, LIFEBIT: {read_plc.life_beat}"
    cv.putText(frame, text, (start, 1 * o), font, font_size, color, 2)
    text = f"POPID {read_plc.popid}, TANK: {read_plc.tank}, PAR: {read_plc.parameter}"
    cv.putText(frame, text, (start, 2 * o), font, font_size, color, 2)
    text = f"DRAIN POSITION {read_plc.drain_position}"
    cv.putText(frame, text, (start, 3 * o), font, font_size, color, 2)
    text = f"STICKER {read_plc.sticker_position}"
    cv.putText(frame, text, (start, 4 * o), font, font_size, color, 2)
    text = f"STICKER POSITION {read_plc.sticker_position}"
    cv.putText(frame, text, (start, 5 * o), font, font_size, color, 2)
    text = f"STICKER ANGLE {read_plc.sticker_position}"
    cv.putText(frame, text, (start, 6 * o), font, font_size, color, 2)
    return frame


def draw_sticker(frame: np.ndarray, camera: Camera, tank: Tank):
    i = 1
    for s in tank.stickers:
        color = color_list[s.label_index]
        text = f"STICKER [{s.label}] X {s.x} Y: {s.y}  "
        text += f"R_X {s.relative_x} R_Y {s.relative_y}  "
        text += f"AREA: {s.area} W: {s.w} H: {s.h}"
        cv.rectangle(frame, (s.x, s.y), (s.x + s.w, s.y + s.h), color, 2)
        font_size = (0.0008 * frame.shape[1])
        x = 20
        y = camera.height - (20 * i)
        cv.putText(frame, text, (x, y), font, font_size, color, 2)
        i += 1
    return frame


def draw_gradient(frame: np.ndarray):
    _, frame = cv.threshold(frame, 127, 255, cv.THRESH_BINARY)
    blur = cv.GaussianBlur(frame, (5, 5), 0)
    blur = cv.bilateralFilter(frame, 9, 75, 75)
    laplacian = cv.Laplacian(blur, cv.CV_64F)
    cv.imshow("Laplace", laplacian)
    return frame


def draw_sobel(frame: np.ndarray):
    _, frame = cv.threshold(frame, 100, 255, cv.THRESH_BINARY)
    blur = cv.GaussianBlur(frame, (3, 3), 0)
    sobelx = cv.Sobel(blur, cv.CV_64F, 0, 1, ksize=3)
    sobely = cv.Sobel(blur, cv.CV_64F, 1, 0, ksize=3)
    cv.imshow("sobel", sobelx)
    return frame


def draw_canny(frame: np.ndarray):
    _, frame = cv.threshold(frame, 50, 255, cv.THRESH_BINARY)
    sigma = 0.5
    v = np.median(frame)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    canny = cv.Canny(frame, lower, upper)
    cv.imshow("Canny", canny)
    cv.imshow("t", frame)
    return frame
