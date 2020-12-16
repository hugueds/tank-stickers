from datetime import datetime
from threading import Thread
from time import sleep
from classes.tank import Tank, Sticker
from models.app_states import AppState
from .plc import PLC
from .camera import Camera

class Controller:

    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    start_time = datetime.now()
    tank: Tank
    thread_plc: Thread

    def __init__(self):
        self.plc = PLC()
        self.camera = Camera()
        self.camera.start()
        self.thread_plc = Thread(name='thread_plc', target=self.update_plc, daemon=True)
        self.thread_plc.start()

    def set_state(self, state: AppState):
        self.state = state

    def update_plc(self):
        print('Starting PLC Thread')
        self.plc.connect()
        while True:
            self.plc.read()
            self.plc.write(self.tank)
            sleep(0.2) # PLC Cycle

    def update_camera(self):
        pass








