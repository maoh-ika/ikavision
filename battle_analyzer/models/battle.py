from enum import Enum
from dataclasses import dataclass

class BattleSide(Enum):
    TEAM = 0
    ENEMY = 1
    NO_SIDE = 2

class BattleRule(Enum):
    UNKNOWN = 99
    NAWABARI = 0
    AREA = 1
    YAGURA = 2
    HOKO = 3
    ASARI = 4

class BattleStage(Enum):
    UNKNOWN = 99
    MAP = 100
    AMABI = 0
    CYOUZAME = 1
    GONZUI = 2
    HIRAME = 3
    KINMEDAI = 4 
    KONBU = 5
    KUSAYA = 6
    MAHIMAHI = 7
    MANTAMARIA = 8
    MASABA = 9
    MATEGAI = 10
    NAMEROU = 11
    NAMPULA = 12
    SUMESHI = 13
    TARAPORT = 14
    YAGARA = 15
    YUNOHANA = 16
    ZATOU = 17
    TAKAASHI = 18
    OHYOU = 19
    BANGAITEI = 20
    NEGITORO = 21
    KAZIKI = 22

class BattleWinLose(Enum):
    WIN = 0
    LOSE = 1
    DRAW = 3

class MatchType(Enum):
    UNKNOWN = 99
    REGULAR_MATCH = 0
    BANKARA_MATCH = 1
    X_MATCH = 2
    EVENT_MATCH = 3
    FES_MATCH = 4
    PRIV_MATCH = 5