from .colors import *
import cv2 as cv
import numpy as np

font = cv.FONT_HERSHEY_SIMPLEX

def draw_roi_lines(frame, camera):
    color = cyan
    (y, x) = frame.shape[:2]
    x_start = int(camera.width * camera.PRC_ROI_X_START // 100)
    x_end =   int(camera.width * camera.PRC_ROI_X_END // 100)
    y_start = int(camera.height * camera.PRC_ROI_Y_START // 100)
    y_end =   int(camera.height * camera.PRC_ROI_Y_END // 100)

    cv.line(frame, (x_start, 0), (x_start, y), color, 2)
    cv.line(frame, (x_end, 0), (x_end, y), color, 2)
    cv.line(frame, (0, y_start), (x, y_start), color, 2)
    cv.line(frame, (0, y_end), (x, y_end), color, 2)
    return frame

def draw_center_axis(frame, camera):
    color = fucshia
    (y, x) = frame.shape[:2]
    x_offset = x // 2 + int(camera.width * camera.PRC_CENTER_X_OFFSET // 100)
    cv.line(frame, (x_offset, 0), (x_offset, y), color)
    cv.line(frame, (0, y // 2), (x, y // 2), color)
    return frame

def draw_camera_info(frame, camera):
    text = f"{frame.shape[1]}x{frame.shape[0]} "
    text += f" FPS: {camera.fps}, FRAME COUNTER: {camera.frame_counter}"
    color = (200, 100, 0)
    cv.putText(frame, text, (20, 20), font, 0.6, color, 2)
    if camera.recording:
        text = f" -- RECORDING --"
        color = (0, 0, 255)
        cv.putText(frame, text, (500, 650), font, 0.7, color, 2)
    return frame

def draw_tank_center_axis(frame, tank):
    x, y, w, h = tank.x, tank.y, tank.w, tank.h
    cv.line(frame, (x, y + (h // 2)), (x + w, y + (h // 2)), red, 1)
    cv.line(frame, (x + (w // 2), y), (x + (w // 2), y + h), red, 1)
    return frame

def draw_tank_rectangle(frame, tank):
    color = tank_color
    x, y, w, h = tank.x, tank.y, tank.w, tank.h
    text = f"TANK WIDTH: {w}, TANK HEIGHT: {h}"
    cv.putText(frame, text, (20, 45), font, 0.6, tank_color, 2)
    cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    return frame

def draw_drain(frame, tank):
    dx, dy, dw, dh = tank.drain_x, tank.drain_y, tank.drain_w, tank.drain_h
    cv.rectangle(frame, (dx, dy), (dx+dw, dy+dh), dark_yellow, 2)
    pt = (int(frame.shape[1] * 0.70), int(frame.shape[0] * 0.07))
    text = f"DRAIN X: {tank.drain_rel_x} Y: {tank.drain_rel_y} AREA: {tank.drain_area}"
    cv.putText(frame,text, pt, font, 0.6, dark_yellow ,2)
    return frame

def draw_plc_status(frame, plc):
    pt = (int(frame.shape[1] * 0.70), int(frame.shape[0] * 0.04))
    color = (128,0,0)
    text = f"PLC STATUS {plc.online}, LIFEBIT: {plc.life_bit}"
    cv.putText(frame, text, pt, font, 0.6, color, 2)
    return frame

def draw_sticker(frame, tank):
    i = 1
    for s in tank.stickers:
        color = color_list[s.label_index]
        text = f"""STICKER {s.label}\
        X: {s.x} Y: {s.y}\
        REL_X: {s.relative_x} REL_Y: {s.relative_y}\
        AREA: {s.area} W: {s.w} H: {s.h}\
            """
        cv.rectangle(frame, (s.x, s.y), (s.x + s.w, s.y + s.h), color, 2)
        cv.putText(frame, text, (100, 700 - (20 * i)), font ,0.6,color,2)
        i += 1
    return frame

def draw_gradient(frame):
    _, frame = cv.threshold(frame, 127, 255, cv.THRESH_BINARY)
    blur = cv.GaussianBlur(frame,(5,5),0)
    blur = cv.bilateralFilter(frame,9,75,75)
    laplacian = cv.Laplacian(blur, cv.CV_64F)
    cv.imshow("Laplace", laplacian)
    return frame

def draw_sobel(frame):
    _, frame = cv.threshold(frame, 100, 255, cv.THRESH_BINARY)
    blur = cv.GaussianBlur(frame,(3,3),0)
    sobelx = cv.Sobel(blur, cv.CV_64F,0,1,ksize=3)
    sobely = cv.Sobel(blur, cv.CV_64F,1,0,ksize=3)
    cv.imshow("sobel", sobelx)
    return frame

def draw_canny(frame):
    _, frame = cv.threshold(frame, 50, 255, cv.THRESH_BINARY)
    sigma = 0.5
    v = np.median(frame)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    canny = cv.Canny(frame,lower,upper)
    cv.imshow("Canny", canny)
    cv.imshow("t", frame)
    return frame


