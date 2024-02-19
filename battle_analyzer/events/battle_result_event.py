from dataclasses import dataclass
from models.battle import BattleWinLose, BattleRule
from prediction.battle_indicator_detection_process import BattleIndicatorDetectionResult, BattleIndicatorDetectionFrame
from prediction.splash_font_ocr import SplashFontOCR
from events.util import find_target_frames, TestResult
from events.battle_open_event import BattleOpenEvent
from events.battle_end_event import BattleEndEvent
from events.battle_countdown_event import BattleCountEvent
from models.battle_indicator import ResultCount
from models.text import to_str
from utils import likely_value, MovieReader

@dataclass
class BattleResultEvent:
    start_frame: int
    end_frame: int
    win_lose: BattleWinLose
    team_count: float
    enemy_count: float

class BattleResultEventCreator:
    def __init__(self,
        battle_movie_path: str,
        open_event: BattleOpenEvent,
        end_event: BattleEndEvent,
        ocr: SplashFontOCR
    ) -> None:
        self.open_event = open_event
        self.end_event = end_event
        self.ocr = ocr
        self.reader = MovieReader(battle_movie_path)

    def create(self, indicator_result: BattleIndicatorDetectionResult) -> BattleResultEvent:
        # first, get win-lose from result frames
        result_event = self._make_from_result(indicator_result)
        if result_event is None:
            # second, from lead label
            result_event = self._make_from_lead_label(indicator_result)

        return result_event

    def _is_result_frame(self, frame: BattleIndicatorDetectionFrame, in_target_frame: bool) -> find_target_frames:
        return TestResult.TARGET if frame.result is not None else TestResult.NOT_TARGET

    def _make_from_result(self, indicator_result: BattleIndicatorDetectionResult) -> BattleResultEvent:
        sliced_result = indicator_result.slice(self.end_event.end_frame)
        result_frames = sliced_result.get_sliced_frames()
        start_idx, end_idx = find_target_frames(result_frames, self._is_result_frame, exit_test_frame_count=30)
        if start_idx is None:
            return None
        
        result_frames = result_frames[start_idx:end_idx+1]
        
        team_count = likely_value(result_frames, self._to_team_count)
        enemy_count = likely_value(result_frames, self._to_enemy_count)
        
        for frame in result_frames:
            if frame.result is not None:
                return BattleResultEvent(
                    start_frame=result_frames[0].frame,
                    end_frame=result_frames[-1].frame,
                    win_lose=frame.result.win_lose,
                    team_count=team_count,
                    enemy_count=enemy_count
                )
            
        return None

    def _make_from_lead_label(self, indicator_result: BattleIndicatorDetectionResult) -> BattleResultEvent:
        sliced_result = indicator_result.slice(self.open_event.end_frame, self.end_event.start_frame)
        for frame in reversed(sliced_result.get_sliced_frames()):
            if frame.indicator is None:
                continue

            if frame.indicator.lead_label is None:
                return None # the last battle indicator should have lead label

            center_x = (frame.indicator.occupancy.xyxy[0] + frame.indicator.occupancy.xyxy[2]) / 2
            win_lose = BattleWinLose.WIN if frame.indicator.lead_label.xyxy[0] < center_x else BattleWinLose.LOSE
            return BattleResultEvent(
                start_frame=self.end_event.end_frame,
                end_frame=self.end_event.end_frame,
                win_lose=win_lose,
                team_count=None,
                enemy_count=None
            )
            
        return None

    def _to_team_count(self, frame: BattleIndicatorDetectionFrame):
        if frame.result is None:
            return None
        if frame.result.team_count.is_percent:
            return self._ocr_result_percent(frame.frame, frame.result.team_count)
        else:
            return self._ocr_result_count(frame.frame, frame.result.team_count)
        
    def _to_enemy_count(self, frame: BattleIndicatorDetectionFrame):
        if frame.result is None:
            return None
        if frame.result.enemy_count.is_percent:
            return self._ocr_result_percent(frame.frame, frame.result.enemy_count)
        else:
            return self._ocr_result_count(frame.frame, frame.result.enemy_count)

    def _ocr_result_count(self, frame: int, count: ResultCount) -> float:
        if count.is_knockout:
            return 100
        img = self.reader.read(frame)
        count_img = img[count.xyxy[1]:count.xyxy[3],count.xyxy[0]:count.xyxy[2]]
        text = to_str(self.ocr.get_number_text(count_img))
        try:
            value = float(text[0:-4]) # remove unit
            return value if value <= 100 else None # count shuld have one or two digits
        except:
            return None
    
    def _ocr_result_percent(self, frame, count: ResultCount) -> float:
        if count.is_knockout:
            return 100
        img = self.reader.read(frame)
        count_img = img[count.xyxy[1]:count.xyxy[3],count.xyxy[0]:count.xyxy[2]]
        text = to_str(self.ocr.get_number_text(count_img))
        text = text[0:-1] # remove percent
        try:
            value = float(text)
            return value if value <= 100 else None
        except:
            return None
    