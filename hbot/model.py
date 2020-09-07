from datetime import datetime, time
from enum import Enum


class Priority(Enum):
    LOW = 1
    SANDARD = 2
    IMPORTANT = 3
    HIGH = 4


class Status(Enum):
    OPEN = 1
    IN_PROGRESS = 2
    CLOSED = 5


class TimeSheet:
    """
    Табель учета рабочего времени
    """
    def __init__(self):
        self.start: datetime  # начало работы
        self.stop: datetime   # окончание работы
        self.time: time       # время работы


class HTask:
    def __init__(self):
        self.id: int = None
        self.descr_1: str = 'Empty description 1'  # work description task 1
        self.descr_2: str = 'Empty description 2'  # work description task 2
        self.address: str = 'Empty address'
        self.added: datetime = datetime.min
        self.priority: Priority = Priority.SANDARD
        self.status: Status = Status.OPEN
        self.closed: datetime = datetime.min
        self.who: str = 'Empty Who'
        self.note: str = ''
