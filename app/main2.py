from time import sleep
from models import AppState
from classes import Controller, Camera


controller = Controller()
controller.set_state(AppState.INITIAL)


while True:
    
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

    
