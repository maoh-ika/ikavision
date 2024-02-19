from enum import Enum, auto
from dataclasses import dataclass
from models.detected_item import DetectedItem
from models.battle import BattleWinLose

class IndicatorNotificationType(Enum):
    COUNT_LEAD = auto()
    COUNT_BEHIND = auto()
    COUNT_STOP = auto()
    COUNT_STOPPED = auto()
    AREA_SECURE = auto()
    AREA_SECURED = auto()
    RESULT_WIN = auto()
    RESULT_LOSE = auto()
    BARRIER_PASS = auto()
    BARRIER_PASSED = auto()
    ASARI_BARRIER_BREAK = auto()
    ASARI_BARRIER_BROKEN = auto()
    ASARI_BARRIER_REPAIR = auto()
    ASARI_BARRIER_REPAIRED = auto()
    HOKO_GET = auto()
    HOKO_LOST = auto()
    HOKO_ROBBED = auto()
    HOKO_STOP = auto()
    YAGURA_GET = auto()
    YAGURA_ROBBED = auto()
    YAGURA_RETURN = auto()
    YAGURA_RETURNED = auto()
    YAGURA_BARRIER_REACH = auto()
    YAGURA_BARRIER_REACHED = auto()

@dataclass
class Count(DetectedItem):
    value: int

    @classmethod
    def from_json(cls, j):
        return cls(**j)

@dataclass
class BattleIndicator:
    counts: list[DetectedItem]
    occupancy: DetectedItem
    lead_label: DetectedItem
    penalties: list[DetectedItem]
    team_asari_counts: list[DetectedItem]
    player_asari_count: DetectedItem
    player_asari_gachi: DetectedItem
    nawabari_paint_point: DetectedItem

    @classmethod
    def from_json(cls, j):
        return cls(
            counts=[DetectedItem.from_json(c) for c in j['counts']],
            occupancy=DetectedItem.from_json(j['occupancy']) if j['occupancy'] is not None else None,
            lead_label=DetectedItem.from_json(j['lead_label']) if j['lead_label'] is not None else None,
            penalties=[DetectedItem.from_json(p) for p in j['penalties']],
            team_asari_counts=[DetectedItem.from_json(c) for c in j['team_asari_counts']],
            player_asari_count=DetectedItem.from_json(j['player_asari_count']) if j['player_asari_count'] is not None else None,
            player_asari_gachi=DetectedItem.from_json(j['player_asari_gachi']) if j['player_asari_gachi'] is not None else None,
            nawabari_paint_point=DetectedItem.from_json(j['nawabari_paint_point']) if j['nawabari_paint_point'] is not None else None,
        )
    
@dataclass
class ResultCount(DetectedItem):
    is_percent: bool
    is_knockout: bool

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        is_percent = jc['is_percent']
        is_knockout = jc['is_knockout']
        del jc['is_percent']
        del jc['is_knockout']
        return cls(
            is_percent=is_percent,
            is_knockout=is_knockout,
            **jc)

@dataclass
class BattleResult:
    team_count: ResultCount
    enemy_count: ResultCount
    win_lose: BattleWinLose

    @classmethod
    def from_json(cls, j):
        return cls(
            team_count=ResultCount.from_json(j['team_count']) if j['team_count'] is not None else None,
            enemy_count=ResultCount.from_json(j['enemy_count']) if j['enemy_count'] is not None else None,
            win_lose=BattleWinLose(j['win_lose']) if j['win_lose'] is not None else None
        )

@dataclass
class IndicatorNotification(DetectedItem):
    type: IndicatorNotificationType
    
    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        type = IndicatorNotificationType(jc['type'])
        del jc['type']
        return cls(
            type=type,
            **jc
        )

@dataclass
class IndicatorNotification(DetectedItem):
    type: IndicatorNotificationType
    
    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        type = IndicatorNotificationType(jc['type'])
        del jc['type']
        return cls(
            type=type,
            **jc
        )
