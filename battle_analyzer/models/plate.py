from dataclasses import dataclass
from models.detected_item import DetectedItem
from models.text import Text

@dataclass
class Badge(DetectedItem):
    
    @classmethod
    def from_json(cls, j):
        return cls(
            xyxy=j['xyxy'],
            conf=j['conf'],
            cls=j['cls'],
        )

@dataclass
class Plate(DetectedItem):
    player_id: Text
    player_name: Text
    nickname: Text
    badges: [Badge]

    @classmethod
    def from_json(cls, j):
        return cls(
            player_id=Text.from_json(j['player_id']) if j['player_id'] else None,
            player_name=Text.from_json(j['player_name']) if j['player_name'] else None,
            nickname=Text.from_json(j['nickname']) if j['nickname'] else None,
            badges=[Badge.from_json(b) for b in j['badges']],
            xyxy=j['xyxy'],
            conf=None,
            cls=j['cls'],
        )