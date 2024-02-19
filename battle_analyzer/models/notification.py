from enum import Enum
from dataclasses import dataclass
from models.detected_item import DetectedItem

class NotificationType(Enum):
    NOTIFICATION_KILL = 0
    NOTIFICATION_DEATH_REASON = 1
    NOTIFICATION_PLAYER_GEAR = 2
    NOTIFICATION_PLAYER_PLATE = 3
    NOTIFICATION_INK_INSUFFICIENT = 4
    NOTIFICATION_RULE_NAWABARI = 5
    NOTIFICATION_RULE_HOKO = 6
    NOTIFICATION_RULE_YAGURA = 7
    NOTIFICATION_RULE_ASARI = 8
    NOTIFICATION_RULE_AREA = 9
    NOTIFICATION_BATTLE_START = 10
    NOTIFICATION_BATTLE_END = 11
    NOTIFICATION_SP_FULLCHARGE = 12
    NOTIFICATION_INK_REFILL = 13
    NOTIFICATION_RULE_TRICOLOR = 14

@dataclass
class Notification(DetectedItem):
    type: NotificationType
    
    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        notif_type = NotificationType(jc['type'])
        del jc['type']
        return cls(
            type=notif_type,
            **jc
        )