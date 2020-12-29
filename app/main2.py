from time import sleep
from models import AppState
from classes import Controller, Camera


# TODO: Take a picture when requested instead of process the image all the time or take 10 pictures

controller = Controller()
controller.set_state(AppState.INITIAL)
sleep(1)
controller.set_state(AppState.PREDICTING_STICKERS)

while True:

    controller.get_frame()

    if controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.PROCESSING_IMAGE)

    elif controller.state == AppState.PROCESSING_IMAGE:
        controller.process() # input number of processed images
        if True:
            controller.set_state(AppState.INITIAL)

    elif controller.state == AppState.INITIAL:
        pass

    controller.process()
    controller.show()
    controller.get_command()