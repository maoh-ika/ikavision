from dataclasses import dataclass
from threading import Thread
from models.battle import BattleSide, BattleRule
from models.battle_info import BattleInfo
from models.battle import BattleSide
from models.text import to_str
from models.detected_item import DetectedItem
from prediction.splash_font_ocr import SplashFontOCR
from prediction.battle_indicator_frame_analyzer import BattleIndicatorAnalysisResult, BattleIndicatorAnalysisFrame
from events.util import taget_frames_generator, TestResult
from utils import MovieReader
from error import InternalError

@dataclass
class BattleCountEvent:
    count: int
    earned_value: int
    side: BattleSide
    start_frame: int
    end_frame: int

class CountMonitor:
    def __init__(self,
        initial_count: int,
        eps: int,
        side: BattleSide,
        ocr: SplashFontOCR,
        reader: MovieReader) -> None:
        self.initial_count = initial_count
        self.cur_count = initial_count
        self.prev_count = initial_count
        self.eps = eps
        self.side = side
        self.ocr = ocr
        self.reader = reader

    def is_current_count_frame(self, frame: BattleIndicatorAnalysisFrame, in_target_frame: bool) -> TestResult:
        raise Exception('no implementation')
    
    def earned_value(self) -> float:
        raise Exception('no implementation')
    
    def _ocr_value(self, frame: int, count: DetectedItem) -> float:
        img = self.reader.read(frame)
        count_img = img[count.xyxy[1]:count.xyxy[3],count.xyxy[0]:count.xyxy[2]]
        lines = self.ocr.get_number_text(count_img, line_break=True)
        return int(to_str(lines[1])) if len(lines) == 2 else None

class CountDownMonitor(CountMonitor):
    def is_current_count_frame(self, frame: BattleIndicatorAnalysisFrame, in_target_frame: bool) -> TestResult:
        indicator = None
        if frame.rule == BattleRule.AREA:
            indicator = frame.area_indicator
        elif frame.rule == BattleRule.HOKO:
            indicator = frame.hoko_indicator
        elif frame.rule == BattleRule.YAGURA:
            indicator = frame.yagura_indicator
        elif frame.rule == BattleRule.ASARI:
            indicator = frame.asari_indicator

        if indicator is None:
            return TestResult.PENDING
        
        if self.side == BattleSide.TEAM:
            count = indicator.team_count
        else:
            count = indicator.enemy_count

        if count is None:
            return TestResult.PENDING
        
        is_current = (self.cur_count <= count or self.cur_count - count >= self.eps)
        if not is_current:
            self.prev_count = self.cur_count
            self.cur_count = count

        return TestResult.TARGET if is_current else TestResult.NOT_TARGET
    
    def earned_value(self) -> float:
        return self.initial_count - self.prev_count

class CountUpMonitor(CountMonitor):
    def is_current_count_frame(self, frame: BattleIndicatorAnalysisFrame, in_target_frame: bool) -> bool:
        indicator = None
        if frame.rule == BattleRule.NAWABARI:
            indicator = frame.nawabari_indicator

        if indicator is None or indicator.paint_point is None:
            return TestResult.PENDING

        is_current = self.cur_count >= indicator.paint_point or (indicator.paint_point - self.cur_count >= self.eps)        
        if not is_current:
            self.prev_count = self.cur_count
            self.cur_count = indicator.paint_point

        return TestResult.TARGET if is_current else TestResult.NOT_TARGET
    
    def earned_value(self) -> float:
        return self.prev_count

class BattleCountEventCreator(Thread):
    def __init__(self, battle_info: BattleInfo, ocr: SplashFontOCR, initial_count: int) -> None:
        super().__init__(name='BattleCountEventCreator')
        self.battle_info = battle_info
        self.ocr = ocr
        self.initial_count = initial_count
        self.indicator_result: BattleIndicatorAnalysisResult = None
        self.events: (list[BattleCountEvent], list[BattleCountEvent]) = None
        self.eps = {
            BattleRule.AREA: 10,
            BattleRule.HOKO: 10,
            BattleRule.YAGURA: 10,
            BattleRule.ASARI: 80,
            BattleRule.NAWABARI: 100

        }

    def create(self, indicator_result: BattleIndicatorAnalysisResult) -> (list[BattleCountEvent], list[BattleCountEvent]):
        self.indicator_result = indicator_result
        self.start()

    def run(self):
        if self.indicator_result is None:
            raise InternalError('run must be called via create')

        team_events = []
        enemy_events = []
        reader = MovieReader(self.battle_info.battle_movie_path)
        eps = self.eps[self.indicator_result.rule]
        if self.indicator_result.rule in [BattleRule.AREA, BattleRule.HOKO, BattleRule.YAGURA, BattleRule.ASARI]:
            team_monitor = CountDownMonitor(self.initial_count, eps, BattleSide.TEAM, self.ocr, reader)
            team_events = self._make_events(self.indicator_result.frames, team_monitor)
            enemy_monitor = CountDownMonitor(self.initial_count, eps, BattleSide.ENEMY, self.ocr, reader)
            enemy_events = self._make_events(self.indicator_result.frames, enemy_monitor)
        elif self.indicator_result.rule == BattleRule.NAWABARI:
            team_monitor = CountUpMonitor(self.initial_count, eps, BattleSide.TEAM, self.ocr, reader)
            team_events = self._make_events(self.indicator_result.frames, team_monitor)
        
        self.events = (team_events, enemy_events)

    def _make_events(self, frames: list[BattleIndicatorAnalysisFrame], monitor: CountMonitor) -> list[BattleCountEvent]:
        events = []
        generator = taget_frames_generator(frames, monitor.is_current_count_frame, exit_test_frame_count=1)
        for count_frames, _, _ in generator:
            if len(count_frames) == 0:
                continue
            event = BattleCountEvent(
                count=monitor.prev_count,
                earned_value=monitor.earned_value(),
                side=monitor.side,
                start_frame=count_frames[0].frame,
                end_frame=count_frames[-1].frame
            )
            events.append(event)

        return events
    