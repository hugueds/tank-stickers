import cv2 as cv
import logging
from datetime import datetime
from configparser import ConfigParser
from .sticker import Sticker
from snap7.client import Client
from snap7.util import *

class PLC:

    db = dict()

    online = False
    reading = False
    life_bit = False
    lock = False
    debug = False

    def __init__(self, config=None):
        parser = ConfigParser()
        parser.read("config.ini")
        config = parser["PLC"]
        self.enabled = True if config["ENABLED"].lower() == 'true' else False
        self.ip = config["IP"]
        self.rack = int(config["RACK"])
        self.slot = int(config["SLOT"])
        self.db["DB_NUMBER"] = int(config["DB_NUMBER"])
        self.db["DB_START"] = int(config["DB_START"])
        self.db["DB_SIZE"] = int(config["DB_SIZE"])
        self.cycle = float(config["CYCLE_TIME"])
        self.debug = int(config["DEBUG"])
        if self.enabled:
            self.client = Client()

    def load_config(self, config):
        pass

    def connect(self):

        if not self.enabled:
            logging.info('PLC is Disabled, change config.ini to start communication')
            return

        if self.client:
            try:
                self.client.connect(self.ip, self.rack, self.slot)                
                self.online = True
                logging.info(f"PLC Connected to {self.ip} Rack {self.rack} Slot {self.slot}")

            except Exception as e:
                logging.error(f"connect::Failed to connect to PLC {self.ip} " + str(e))

    def write(self, tank):
        
        if self.lock or not self.enabled:
            return False

        self.reading = True
        self.life_bit = not self.life_bit

        label = ' '
        quantity = len(tank.stickers)       
        position = 0
        x, y, angle, quadrant = 0, 0, 0, 0

        if quantity:
            sticker = tank.stickers[0]
            label = sticker.label.split("_")[0]
            x = sticker.relative_x
            y = sticker.relative_y
            position = sticker.position
            quadrant = sticker.quadrant
            angle = int(sticker.angle)            

        height = tank.h
        width = tank.w
        last_update = datetime.now()        
        
        if tank.drain_found:
            drain_x = tank.drain_rel_x
            drain_y = tank.drain_rel_y
        else:
            drain_x, drain_y = 0, 0

        if self.debug:            
            print(f"LABEL {label} POSITION {position}  QUANTITY {quantity}")
            print(f"W {width}  H {height}  X {x} Y {y} ANGLE {angle}, D_X {drain_x} D_Y {drain_y}")
            return 

        try:
            lock = True
            data = bytearray(self.db["DB_SIZE"])
            
            # data[0] = 7 if self.life_bit else 5
            # 000001X0 -> 0.0 = Reading, 0.1 = Lifebit, 0.2 = Always True, 0.3 = Drain
            data[0] = (tank.drain_found << 3) + (1 << 2) + (self.life_bit << 1) + (self.reading << 0)
            data[1] = int.from_bytes(label.encode(), "big")
            data[2] = position

            set_int(data, 4, quadrant)
            set_int(data, 6, height)
            set_int(data, 8, width)
            set_int(data, 10, x)
            set_int(data, 12, y)
            set_int(data, 14, quantity)
            # set_int(data, 16, angle)
            set_int(data, 16, position) # Replace after PLC update
            set_int(data, 18, drain_x)
            set_int(data, 20, drain_y)

            self.client.db_write(
                db_number=self.db["DB_NUMBER"], start=self.db["DB_START"], data=data
            )

        except Exception as e:
            self.online = False
            print("Error::PLC::write => " + str(e))            

        finally:
            self.lock = False

    def clean_values(self):

        if self.lock or not self.enabled:
            return False

        self.reading = False
        self.life_bit = not self.life_bit

        try:
            lock = True
            data = bytearray(self.db["DB_SIZE"])

            # 000001X0 -> 0.0 = Reading, 0.1 = Lifebit, 0.2 = Always True, 0.3 = Drain
            data[0] = (0 << 3) + (1 << 2) + (self.life_bit << 1) + (self.reading << 0)
            data[1] = int.from_bytes("".encode(), "big")
            data[2] = 0

            set_int(data, 4, 0)
            set_int(data, 6, 0)
            set_int(data, 8, 0)
            set_int(data, 10, 0)
            set_int(data, 12, 0)
            set_int(data, 14, 0)
            set_int(data, 16, 0)
            set_int(data, 18, 0)
            set_int(data, 20, 0)

            self.client.db_write(
                db_number=self.db["DB_NUMBER"], start=self.db["DB_START"], data=data
            )

        except Exception as e:
            self.online = False            
            logging.error("Error::clean_values " + str(e))

        finally:
            self.lock = False

    def check_connection(self):
        if not self.enabled:
            return False

        logging.info('Checking PLC Connection')        

        try:
            res = self.client.db_read(
                db_number=self.db["DB_NUMBER"], start=0, size=1)
            
            if not res:
                Exception('Error at reading PLC values')
            else:
                self.online = True

        except Exception as e:
            logging.error("Error::check_connection" + str(e))
            self.online = False
            self.disconnect()
            self.connect()

    
    def disconnect(self):
        # self.client.disconnect()
        pass

