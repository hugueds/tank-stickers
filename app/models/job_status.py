from enum import Enum

class JobStatus(Enum):
    INITIAL = 0
    RUNNING = 1
    DONE = 2
    CANCELLED = 3
