from enum import Enum

class AppState(Enum):
    INITIAL = 0
    ERROR = -1
    WAITING_REQUEST = 2
    PROCESSING_IMAGE = 2
    FINDING_TANK = 3
    FINDING_DRAIN = 4
    FINDING_STICKERS = 5
    PREDICTING_STICKERS = 6
    SAVING_RESULTS = 7

