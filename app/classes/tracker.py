from classes import Camera
from classes import Tank

class Tracker:

    def __init__(self, camera:Camera, tank: Tank):
        self.camera = camera
        self.tank = tank

    def update_tank_tracker(self, key, value):
        setattr(self.tank, key, value)

    def update_camera_config(self, key, value):
        setattr(self.camera, key, value)

    def update(self, key, value):
        pass

    def open(self):
        pass

    def close(self):
        pass


