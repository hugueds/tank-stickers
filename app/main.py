from time import sleep
from models import AppState
from classes import Controller

controller = Controller()

while True:

    controller.get_frame()
    controller.check_skid()
    controller.process()

    if controller.state == AppState.INITIAL:
        sleep(1)
        controller.start_plc()
        controller.set_state(AppState.WAITING_REQUEST)

    elif controller.state == AppState.WAITING_REQUEST:
        if controller.new_request():
            controller.confirm_request()            
            controller.set_state(AppState.PROCESSING_IMAGE)

    elif controller.state == AppState.PROCESSING_IMAGE:
        controller.analyse()
        if controller.final_result:
            controller.set_state(AppState.SAVING_RESULTS)
        elif controller.new_request():
            print('Aborting current Job...')
            controller.abort_job()
            controller.set_state(AppState.WAITING_REQUEST)
        else:
            print('Invalid Configuration, redoing operation')
            sleep(0.1)

    elif controller.state == AppState.SAVING_RESULTS:
        controller.save_result()
        controller.set_state(AppState.WAITING_REQUEST)

    controller.show()
    controller.get_command()
