from enum import IntEnum

class JobStatus(IntEnum):
    INITIAL = 0
    RUNNING = 1
    DONE = 2
    CANCELLED = 3
