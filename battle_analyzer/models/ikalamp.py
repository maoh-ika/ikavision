from enum import Enum
from dataclasses import dataclass
from models.battle import BattleSide
from models.detected_item import DetectedItem

class IkalampState(Enum):
    LIVE = 0
    DEATH = 1
    SP = 2
    DROP = 3

@dataclass
class Ikalamp(DetectedItem):
    side: BattleSide
    state: IkalampState
    ord: int
    
    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        side = BattleSide(jc['side'])
        state = IkalampState(jc['state'])
        del jc['side']
        del jc['state']

        return cls(
            side=side,
            state=state,
            **jc
        )

class IkalampTimerState(Enum):
    INTERVAL = 0
    MATCH = 1
    EXTRA = 2

@dataclass
class IkalampTimer(DetectedItem):
    state: IkalampTimerState

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        state = IkalampTimerState(jc['state'])
        del jc['state']
        return cls(
            state=state,
            **jc
        )