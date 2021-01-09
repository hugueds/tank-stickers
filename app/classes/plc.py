from snap7.client import Client
from snap7.util import *
from time import sleep
import yaml
from threading import Thread
from datetime import datetime
from classes import Sticker, Tank, camera
from models import PLCInterface, PLCWriteInterface
from logger import logger

class PLC:

    online = False
    reading = False
    lock = False
    debug = False
    read_bytes: bytearray
    interface: PLCInterface
    thread: Thread
    camera: int

    def __init__(self, camera_number, config_file='config.yml'):
        self.load_config(config_file)
        self.camera_number = camera_number
        self.client = Client()

    def load_config(self, config_file='config.yml'):
        with open(config_file) as file:
            config = yaml.safe_load(file)['plc']
        self.enabled = config['enabled']
        self.ip = config['ip']
        self.rack = config['rack']
        self.slot = config['slot']
        self.db_read: dict = config['db_read']
        self.db_write: dict = config['db_write']
        self.update_time = config['update_time']
        self.debug = config['debug']

    def connect(self):

        if not self.enabled:
            return logger.info('PLC is Disabled, change config file to start communication')

        if self.client:
            try:
                self.client.connect(self.ip, self.rack, self.slot)
                self.online = True
                logging.info(f"PLC Connected to {self.ip} Rack {self.rack} Slot {self.slot}")
            except Exception as e:
                logging.exception(f"connect::Failed to connect to PLC {self.ip} " + str(e))

    def read(self):
        try:
            db = self.db_read
            start = db['size'] * self.camera_number
            return self.client.db_read(db['number'], start, db['size'])
        except Exception as e:
            logger.exception(e)

    def write(self, data: PLCWriteInterface):
        try:
            _bytearray = data.get_bytearray()
            db = self.db_write
            start = db['size'] * self.camera_number
            self.client.db_write(db['number'], start, _bytearray)
        except Exception as e:
            logger.exception(e)

    def disconnect(self):
        self.online = False
        self.client.disconnect()

