from enum import Enum
from dataclasses import dataclass
import numpy as np
from models.ikalamp import BattleSide
from models.detected_item import TrackableItem, SegmentItem

class IkaPlayerState(Enum):
    LIVE = 0
    DEATH = 1
    DROP = 2

class IkaPlayerForm(Enum):
    HITO = 0
    IKA = 1
    IKAROLL = 2
    IKADASH = 3
    HITO_FAR = 4
    HITO_MAIN = 5
    HITO_SUB = 6
    HITO_SP = 7

@dataclass
class IkaPlayerPosition(TrackableItem):
    form: IkaPlayerForm

    @classmethod
    def from_json(cls, j):
        return cls(
            xyxy=j['xyxy'],
            form=IkaPlayerForm(j['form']),
            conf=j['conf'],
            cls=j['cls'],
            track_id=j['track_id']
        )
    
@dataclass
class IkaPlayer:
    id: str
    name: str
    nickname: str
    side: BattleSide
    lamp_ord: int

@dataclass
class InkTank:
    ink_level: float
    consumed: SegmentItem
    remaining: SegmentItem

    @classmethod
    def from_json(cls, j):
        return cls(
            ink_level=j['ink_level'],
            consumed=SegmentItem.from_json(j['consumed']),
            remaining=SegmentItem.from_json(j['remaining'])
        )