class Tracker:

    def __init__(self, camera, tank):
        self.camera = camera
        self.tank = tank

    def update_tank_tracker(self, key, value):
        setattr(self.tank, key, value)

    def update_camera_config(self, key, value):
        setattr(self.camera, key, value)

