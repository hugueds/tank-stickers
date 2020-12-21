from time import sleep
from models import AppState
from classes import Controller, Camera


# TODO: Take a picture when requested instead of process the image all the time or take 10 pictures


controller = Controller()
controller.set_state(AppState.INITIAL)


while True:
    
    controller.get_frame()
    controller.show()    
    controller.get_command()

    if controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.INITIAL)

    elif controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.INITIAL)

    elif controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.INITIAL)

    elif controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.INITIAL)

    elif controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.INITIAL)

    elif controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.INITIAL)

    elif controller.state == AppState.INITIAL:
        if True:
            controller.set_state(AppState.INITIAL)

    
