from dataclasses import dataclass
from prediction.ikalamp_detection_process import IkalampDetectionResult
from prediction.ika_player_detection_process import IkaPlayerDetectionResult
from prediction.player_position_frame_analyzer import PlayerPositionAnalysisResult
from prediction.ink_tank_frame_analyzer import InkTankAnalysisResult
from events.player_number_balance_event import PlayerNumberBalanceEvent
from stream.candle_chart import CandleChart

@dataclass
class State:
    frame_number: int
    ikalamp: IkalampDetectionResult = None
    ika: IkaPlayerDetectionResult = None
    main_player_position: PlayerPositionAnalysisResult = None
    ink_tank: InkTankAnalysisResult = None
    ink_tank_chart = CandleChart(candle_count=-1, candle_period=30, fill_with_blank=False)
    number_balance_event: PlayerNumberBalanceEvent = None
