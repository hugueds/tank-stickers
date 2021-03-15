from time import sleep
from models import AppState
from classes import Controller

controller = Controller()

while True:

    controller.get_frame()
    controller.process()

    if controller.state == AppState.INITIAL:
        sleep(1)
        controller.start_plc()
        controller.set_state(AppState.WAITING_REQUEST)

    elif controller.state == AppState.WAITING_REQUEST:

        if not controller.tank.found or controller.read_plc.skid == 0:
            controller.write_plc.cam_status = 0
            controller.write_plc.job_status = 0

        if controller.read_plc.read_request:
            print('New Job Request')
            controller.confirm_request()
            sleep(1)
            controller.set_state(AppState.PROCESSING_IMAGE)

    elif controller.state == AppState.PROCESSING_IMAGE:
        controller.analyse()
        if controller.final_result:
            controller.set_state(AppState.SAVING_RESULTS)
        elif controller.read_plc.read_request:
            print('Aborting current Job...')
            controller.write_plc.job_status = 0
            controller.set_state(AppState.WAITING_REQUEST)
        else:
            print('Invalid Configuration, redoing operation')
            sleep(0.1)

    elif controller.state == AppState.SAVING_RESULTS:
        controller.save_result()
        controller.set_state(AppState.WAITING_REQUEST)

    controller.show()
    controller.get_command()
