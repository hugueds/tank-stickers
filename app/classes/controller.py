from datetime import datetime
from time import sleep
from models.app_states import AppState
from .plc import PLC
from .camera import Camera

class Controller:

    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    start_time = datetime.now()

    def __init__(self):
        plc = PLC()
        camera = Camera()
        camera.start()

    def set_state(self, state: AppState):
        self.state = state








