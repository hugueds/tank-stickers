import os
import argparse
import cv2 as cv 
import numpy as np
from time import sleep
from tracker import Tracker

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="source of the stream")
parser.add_argument("--filter", help="filter type -- HSV, RGB, LAB", default='hsv')
args = parser.parse_args()

if args.path:
    path = args.path
else:
    path = cv.CAP_DSHOW
    path = 0

if args.filter:
    camera_filter = args.filter
else:
    camera_filter = None

FPS = 10
SKIP_FRAMES = 50
WIDTH = 1280
HEIGHT = 720
FONT = cv.FONT_HERSHEY_COMPLEX
FILTER = 'lab'


cap = cv.VideoCapture(path)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)
cv.namedWindow('Main')
cv.resizeWindow('Main', (WIDTH, HEIGHT))
total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

print('ok 1')

initial_lh, initial_hh = 120,220
initial_ls, initial_hs = 122, 140
initial_lv, initial_hv = 135, 160

t = Tracker(initial_lh, initial_hh, initial_ls, initial_hs, initial_lv, initial_hv)

# TRACKER INIT

cv.namedWindow('Tracker')
cv.resizeWindow('Tracker', 600,600)
cv.createTrackbar("L-H", 'Tracker', initial_lh, 255, lambda eventValue, name='l_h': t.update(value=eventValue, name=name))
cv.createTrackbar("H-H", 'Tracker', initial_hh, 360, lambda eventValue, name='h_h': t.update(value=eventValue, name=name))
cv.createTrackbar("L-S", 'Tracker', initial_ls, 255, lambda eventValue, name='l_s': t.update(value=eventValue, name=name))
cv.createTrackbar("H-S", 'Tracker', initial_hs, 255, lambda eventValue, name='h_s': t.update(value=eventValue, name=name))
cv.createTrackbar("L-V", 'Tracker', initial_lv, 255, lambda eventValue, name='l_v': t.update(value=eventValue, name=name))
cv.createTrackbar("H-V", 'Tracker', initial_hv, 255, lambda eventValue, name='h_v': t.update(value=eventValue, name=name))

cv.createTrackbar("Thereshold_Min", 'Tracker', 127, 255, lambda eventValue, name='threshold_min': t.update(value=eventValue, name=name))
cv.createTrackbar("Thereshold_Max", 'Tracker', 255, 255, lambda eventValue, name='threshold_man': t.update(value=eventValue, name=name))

cv.createTrackbar("Blur", 'Tracker', 1, 31, lambda eventValue, name='blur': t.updateKernel(value=eventValue, name=name))
cv.createTrackbar("Erode", 'Tracker', 1, 31, lambda eventValue, name='erode': t.updateKernel(value=eventValue, name=name))
cv.createTrackbar("Dilate", 'Tracker', 1, 31, lambda eventValue, name='dilate': t.updateKernel(value=eventValue, name=name))

cv.createTrackbar("Canny_Min", 'Tracker', 0, 255, lambda eventValue, name='canny_max': t.update(value=eventValue, name=name))
cv.createTrackbar("Canny_Max", 'Tracker', 255, 255, lambda eventValue, name='canny_min': t.update(value=eventValue, name=name))

cv.createTrackbar("FPS", 'Tracker', 30, 60, lambda eventValue, name='fps': t.update(value=eventValue, name=name))
cv.createTrackbar("PAUSE", 'Tracker', 0, 1, lambda eventValue, name='pause': t.update(value=eventValue, name=name))

enabled = 1

while enabled and cap.isOpened():

    print('ok')
    
    # Get Image
    
    if not t.pause:
        suc, frame = cap.read()       
        print(suc)   
        current_frame = cap.get(cv.CAP_PROP_POS_FRAMES)        
        g_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)       

        if camera_filter == 'rgb':
            filter_frame = frame
        elif camera_filter == 'hsv':
            filter_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        elif camera_filter == 'lab':
            filter_frame = cv.cvtColor(frame, cv.COLOR_BGR2LAB)
        else:
            filter_frame = frame

    # Filter    
    mask, masked = t.getMask(filter_frame)
    # Display     
    text = 'W: {}, H: {}, FPS: {}, FRAME: {}'.format(frame.shape[1], frame.shape[0], t.fps, current_frame)
    cv.putText(frame, text, (10, 15), FONT, 0.6, (255,0,0), 1)
    
    frame = frame / 255

    cv.imshow('Main', frame)
    cv.imshow('Mask', mask)
    # cv.imshow('Thres', thres)
    # cv.imshow('Masked', masked)
    # cv.imshow('LAB', lab_frame)
    # cv.imshow('Canny', canny)
    # cv.imshow('Lap', lap)
    # cv.imshow('Sobel_X', sobel_x)
    # cv.imshow('Sobel_Y', sobel_y)
    # cv.imshow('Blended', blended)
    # cv.imshow('Gradient', gradient)
    
    if t.fps > 0:
        sleep(1/t.fps)

    if current_frame >= total_frames - 1:        
        cap.set(cv.CAP_PROP_POS_FRAMES, 0)
    
    # Control
        
    key = cv.waitKey(1)
    
    if key == ord('s'):               
        files = len([name for name in os.listdir('./captures')])                
        path = 'captures/' + str(files).zfill(3) + '.jpg'
        cv.imwrite(path, frame)   
        
    elif key == ord('p'):        
        t.pause = abs(t.pause - 1)
        
    elif key == ord('f'):
        # Save filters in NP mode [ [[low_hsv], [high_hsv]], threshold, blur_kernel]
        print(t.l_h, t.l_s, t.l_v)
        print(t.h_h, t.h_s, t.h_v)
        np.save('filters.npy', ((t.l_h, t.l_s, t.l_v), (t.h_h, t.h_s, t.h_v)) )
        
    elif key == ord('+'):        
        cap.set(cv.CAP_PROP_POS_FRAMES, current_frame + SKIP_FRAMES)
        _, frame = cap.read()
        
    elif key == ord('-'):
        current_frame = cap.get(cv.CAP_PROP_POS_FRAMES)
        if current_frame > 100:
            cap.set(cv.CAP_PROP_POS_FRAMES, current_frame - SKIP_FRAMES)
            _, frame = cap.read()
    
    elif key == 27 or key == ord('q'):
        enabled = False
        

# Closing
    
cap.release()
cv.destroyAllWindows()
exit(0)
