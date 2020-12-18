from datetime import datetime
from models import PLCInterface
from threading import Thread
from time import sleep
from classes.tank import Tank, Sticker
from models.app_states import AppState
from .plc import PLC
from .camera import Camera
import keyboard

class Controller:

    state: AppState = AppState.INITIAL
    camera: Camera
    plc: PLC
    plc_interface: PLCInterface
    start_time = datetime.now()
    tank: Tank
    thread_plc: Thread
    thread_camera: Thread
    camera_enabled = True


    def __init__(self):
        self.plc = PLC()
        self.camera = Camera()
        self.camera.start()
        self.thread_plc = Thread(name='thread_plc', target=self.update_plc, daemon=True)
        self.thread_plc.start()        
        keyboard.on_press(self.on_press)

    def start_camera(self):
        Thread(name='thread_camera', target=self.update_camera, daemon=True).start()
        self.start_camera()


    def set_state(self, state: AppState):
        self.state = state

    def update_plc(self):
        print('Starting PLC Thread')
        self.plc.connect()
        while self.plc.enabled:
            self.plc.read()
            self.plc.write(self.tank)
            sleep(0.2) # PLC Cycle
        else:
            print('PLC is not enabled')

    def update_camera(self):
        print('Starting Camera Update')        

        while self.camera_enabled:
            frame = self.camera.read()
            self.camera.show(frame)
        else:
            print('Camera update ended')


    def on_press(self, e: keyboard.KeyboardEvent):
        print(e.name)
        if e.name == 'q':
            self.camera_enabled = False
        elif e.name == 's':
            self.camera_enabled = True
            Thread(name='thread_camera', target=self.update_camera, daemon=True).start()


    def save_result(self):
        pass








