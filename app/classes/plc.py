from snap7.client import Client
from snap7.util import *
import yaml
from logger import logger

class PLC:

    online = False
    debug = False
    camera_number: int

    def __init__(self, camera_number, config_file='config.yml') -> None:
        self.load_config(config_file)
        self.camera_number = camera_number
        self.client = Client()

    def load_config(self, config_file='config.yml') -> None:
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

    def connect(self) -> None:

        if not self.enabled:
            return logger.info('PLC is Disabled, change config file to start communication')

        if self.client:
            try:
                self.client.connect(self.ip, self.rack, self.slot)
                self.online = True
                logging.info(f"PLC Connected to {self.ip} Rack {self.rack} Slot {self.slot}")
            except Exception as e:
                logging.exception(f"connect::Failed to connect to PLC {self.ip} " + str(e))

    def read(self) -> bytearray:
        try:
            db = self.db_read
            start = db['size'] * self.camera_number
            return self.client.db_read(db['number'], start, db['size'])
        except Exception as e:
            logger.exception(e)

    def write(self, _bytearray: bytearray) -> None:
        try:
            db = self.db_write
            start = db['size'] * self.camera_number
            self.client.db_write(db['number'], start, _bytearray)
        except Exception as e:
            logger.exception(e)

    def disconnect(self):
        self.online = False
        self.client.disconnect()

