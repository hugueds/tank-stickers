from enum import IntEnum

class AppState(IntEnum):
    INITIAL = 0    
    WAITING_REQUEST = 1
    PROCESSING_IMAGE = 2    
    SAVING_RESULTS = 3
    FINISHED = 4

