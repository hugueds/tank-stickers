from enum import Enum

class AppState(Enum):
    INITIAL = 0    
    WAITING_REQUEST = 1
    PROCESSING_IMAGE = 2    
    SAVING_RESULTS = 3
    FINISHED = 4

