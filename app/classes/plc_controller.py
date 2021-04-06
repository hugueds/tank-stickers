from threading import Thread
from time import sleep
from classes.plc import PLC
from models import PLCInterface, PLCWriteInterface, Deviation, JobStatus

class PlcController():

    plc: PLC
    read_data: PLCInterface
    write_data: PLCWriteInterface
    thread_enabled = False

    def __init__(self, camera_number=0, config_file='') -> None:
        self.plc = PLC(camera_number, config_file)
        self.read_data = PLCInterface()
        self.write_data = PLCWriteInterface(self.plc.db_write['size'])


    def start(self):
        self.plc.connect()
        self.thread_enabled = True
        Thread(name='thread_plc', target=self.update_plc, daemon=True).start()

    def stop(self):
        self.thread_enabled = False

    def update_plc(self) -> None:
        last_life_beat = -1
        while self.plc.enabled and self.thread_enabled:
            data = self.plc.read()
            self.read_data.update(data)
            if self.read_data.life_beat == last_life_beat:
                # logger.error('PLC is not responding... Trying to reconnect')
                print('PLC is not responding... Trying to reconnect')
                self.plc.disconnect()
                sleep(5)
                self.plc.connect()
            else:
                last_life_beat = self.read_data.life_beat
                self.write_data.update_life_beat()
                _bytearray = self.write_data.get_bytearray()
                self.plc.write(_bytearray)
                sleep(self.plc.update_time)
        else:
            # logger.warning('PLC is not Enabled')
            print('PLC not enabled')


    def job_done(self):
        self.write_data.cam_status = 1
        self.write_data.job_status = JobStatus.DONE
        self.write_data.request_ack = False

    def abort_job(self):
        self.__clear_plc()
        self.write_data.cam_status = Deviation.TANK_NOT_FOUND
        self.write_data.job_status = JobStatus.CANCELLED

    def clear_plc(self):
        self.write_data.position_inc_drain = 0
        self.write_data.position_inc_sticker = 0
        self.write_data.inc_sticker = 0
        self.write_data.inc_angle = 0

    def confirm_request(self):
        print('New Job Request: ', self.read_data.request_number)
        print(f'SKID: {self.read_data.skid}, POPID: {self.read_data.popid}')
        print(f'TANK: {self.read_data.partnumber} PARAMETER: {self.read_data.parameter}')
        print(f'STICKER: {self.read_data.sticker}, ANGLE: {self.read_data.sticker_angle}, DRAIN: {self.read_data.drain_position}')
        self.last_request = self.read_data.request_number
        self.read_data.read_request = False
        self.write_data.request_ack = True
        self.write_data.cam_status = Deviation.TANK_NOT_FOUND
        self.write_data.job_status = int(JobStatus.RUNNING)
        self.final_result = False
        self.analyse_counter = 0
        self.result_list.clear()
        sleep(1)

    def __print_plc_values(self) -> None:
        print('PLC READ:')
        print(self.read_data.__dict__)
        print('\nPLC WRITE:')
        print(self.write_data.__dict__)