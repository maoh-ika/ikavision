from dataclasses import dataclass
from threading import Thread
from ultralytics import YOLO
import torch
import cv2
import numpy as np
from prediction.battle_indicator_detection_process import BattleIndicatorDetectionResult, BattleIndicatorDetectionFrame
from prediction.prediction_process import preprocess
from prediction.splash_font_ocr import SplashFontOCR
from models.ika_player import IkaPlayerPosition, InkTank 
from models.detected_item import DetectedItem
from models.text import to_str
from models.battle_info import BattleInfo
from models.battle import BattleSide, BattleRule, BattleWinLose
from models.ink_color import InkColor
from models.battle_indicator import ResultCount
from utils import MovieReader
from error import InternalError

@dataclass
class NawabariIndicator:
    paint_point: int

@dataclass
class AreaIndicator:
    team_count: int
    enemy_count: int
    team_penalty: int
    enemy_penalty: int
    lead_side: BattleSide

@dataclass
class HokoIndicator:
    team_count: int
    enemy_count: int
    lead_side: BattleSide

@dataclass
class YagraIndicator:
    team_count: int
    enemy_count: int
    lead_side: BattleSide

@dataclass
class AsariIndicator:
    team_count: int
    enemy_count: int
    team_penalty: int
    enemy_penalty: int
    lead_side: BattleSide
    team_asari_count: int
    enemy_asari_count: int
    player_asari_count: int
    has_player_gachi: int

@dataclass
class BattleResult:
    team_count: float
    enemy_count: float
    is_percent: bool
    win_lose: BattleWinLose

@dataclass
class BattleIndicatorAnalysisFrame:
    frame: int
    rule: BattleRule
    nawabari_indicator: NawabariIndicator=None
    area_indicator: AreaIndicator=None
    hoko_indicator: HokoIndicator=None
    yagura_indicator: YagraIndicator=None
    asari_indicator: AsariIndicator=None
    
@dataclass
class BattleIndicatorAnalysisResult:
    frames: list[BattleIndicatorAnalysisFrame] 
    rule: BattleRule
    
class BattleIndicatorFrameAnalyzer(Thread):
    def __init__(self,
            battle_info: BattleInfo,
            ocr: SplashFontOCR
        ) -> None:
        super().__init__(name='BattleIndicatorFrameAnalyzer')
        self.team_color = battle_info.team_color
        self.enemy_color = battle_info.enemy_color
        self.rule = battle_info.rule
        self.ocr = ocr
        self.reader = MovieReader(battle_info.battle_movie_path)
        self.battle_indicator_result: BattleIndicatorDetectionResult = None
        for ikalamp in battle_info.ikalamp.get_sliced_frames():
            if ikalamp.timer:
                self.timer = ikalamp.timer
                break
        self.result: BattleIndicatorAnalysisResult = None

    def analyze(self, battle_indicator_result: BattleIndicatorDetectionResult) -> BattleIndicatorAnalysisResult:
        self.battle_indicator_result = battle_indicator_result
        self.start()

    def run(self):
        if self.battle_indicator_result is None:
            raise InternalError('run must be called via analyze')
        res_frames = []
        frames = self.battle_indicator_result.get_sliced_frames()
        for idx in range(0, len(frames), 3):
            indicator_frame = frames[idx]
            frame = None
            if indicator_frame.indicator:
                if self.rule == BattleRule.AREA:
                    frame = self._analyze_area_indicator(indicator_frame)
                elif self.rule == BattleRule.HOKO:
                    frame = self._analyze_hoko_indicator(indicator_frame)
                elif self.rule == BattleRule.YAGURA:
                    frame = self._analyze_yagura_indicator(indicator_frame)
                elif self.rule == BattleRule.ASARI:
                    frame = self._analyze_asari_indicator(indicator_frame)
                elif self.rule == BattleRule.NAWABARI:
                    frame = self._analyze_nawabari_indicator(indicator_frame)
                else:
                    frame = None

            if frame:
                res_frames.append(frame)
        
        self.result = BattleIndicatorAnalysisResult(frames=res_frames, rule=self.rule)

    def _analyze_area_indicator(self, frame: BattleIndicatorDetectionFrame) -> BattleIndicatorAnalysisFrame:
        if len(frame.indicator.counts) != 2 or frame.indicator.occupancy is None:
            return None
        
        center_x = (frame.indicator.occupancy.xyxy[0] + frame.indicator.occupancy.xyxy[2]) / 2
        team_count, enemy_count = self._analyze_rest_count(frame, center_x)
        team_penalty, enemy_penalty = self._analyze_penalty(frame, center_x)
        lead_side = self._lead_side(frame, center_x)

        indicator = AreaIndicator(
            team_count=team_count,
            enemy_count=enemy_count,
            team_penalty=team_penalty,
            enemy_penalty=enemy_penalty,
            lead_side=lead_side
        )
        return BattleIndicatorAnalysisFrame(frame=frame.frame, rule=self.rule, area_indicator=indicator)
    
    def _analyze_hoko_indicator(self, frame: BattleIndicatorDetectionFrame) -> BattleIndicatorAnalysisFrame:
        if len(frame.indicator.counts) > 2 or self.timer is None:
            return None

        team_count, enemy_count = self._analyze_progress_count(frame)
        
        center_x = (self.timer.xyxy[0] + self.timer.xyxy[2]) / 2
        lead_side = self._lead_side(frame, center_x)
        
        indicator = HokoIndicator(
            team_count=team_count,
            enemy_count=enemy_count,
            lead_side=lead_side
        )
        return BattleIndicatorAnalysisFrame(frame=frame.frame, rule=self.rule, hoko_indicator=indicator)
    
    def _analyze_yagura_indicator(self, frame: BattleIndicatorDetectionFrame) -> BattleIndicatorAnalysisFrame:
        if len(frame.indicator.counts) > 2 or self.timer is None:
            return None
        
        team_count, enemy_count = self._analyze_progress_count(frame)
        
        center_x = (self.timer.xyxy[0] + self.timer.xyxy[2]) / 2
        lead_side = self._lead_side(frame, center_x)
        
        indicator = YagraIndicator(
            team_count=team_count,
            enemy_count=enemy_count,
            lead_side=lead_side
        )
        return BattleIndicatorAnalysisFrame(frame=frame.frame, rule=self.rule, yagura_indicator=indicator)
    
    def _analyze_asari_indicator(self, frame: BattleIndicatorDetectionFrame) -> BattleIndicatorAnalysisFrame:
        if len(frame.indicator.counts) != 2 or len(frame.indicator.team_asari_counts) != 2:
            return None
        if frame.indicator.player_asari_count is None and frame.indicator.player_asari_gachi is None:
            return None

        center_x = (self.timer.xyxy[0] + self.timer.xyxy[2]) / 2
        team_count, enemy_count = self._analyze_rest_count(frame, center_x)
        team_penalty, enemy_penalty = self._analyze_penalty(frame, center_x)
        lead_side = self._lead_side(frame, center_x)

        team_asari_count = self._ocr_value(frame.frame, frame.indicator.team_asari_counts[0])
        if team_asari_count is None or team_asari_count > 32:
            return None
        enemy_asari_count = self._ocr_value(frame.frame, frame.indicator.team_asari_counts[1])
        if enemy_asari_count is None or enemy_asari_count > 32:
            return None

        has_gachi = False
        if frame.indicator.player_asari_gachi is not None:
            has_gachi = True
            asari_count = 8
        else:
            asari_count = self._ocr_value(frame.frame, frame.indicator.player_asari_count)
            if asari_count is None or asari_count > 7:
                return None

        indicator = AsariIndicator(
            team_count=team_count,
            enemy_count=enemy_count,
            team_penalty=team_penalty,
            enemy_penalty=enemy_penalty,
            lead_side=lead_side,
            team_asari_count=team_asari_count,
            enemy_asari_count=enemy_asari_count,
            player_asari_count=asari_count,
            has_player_gachi=has_gachi
        )
        return BattleIndicatorAnalysisFrame(frame=frame.frame, rule=self.rule, asari_indicator=indicator)
    
    def _analyze_nawabari_indicator(self, frame: BattleIndicatorDetectionFrame) -> BattleIndicatorAnalysisFrame:
        if frame.indicator.nawabari_paint_point is None:
            return None

        point = self._ocr_paint_point(frame.frame, frame.indicator.nawabari_paint_point)
        if point is None:
            return None
        
        indicator = NawabariIndicator(paint_point=point)
        
        return BattleIndicatorAnalysisFrame(frame=frame.frame, rule=self.rule, nawabari_indicator=indicator)

    def _lead_side(self, frame: BattleIndicatorDetectionFrame, base_x: int) -> BattleSide:
        lead_side = BattleSide.NO_SIDE
        if frame.indicator.lead_label:
            lead_side = BattleSide.TEAM if frame.indicator.lead_label.xyxy[0] < base_x else BattleSide.ENEMY
        return lead_side

    def _analyze_result(self, frame: BattleIndicatorDetectionFrame) -> BattleResult:
        if frame.result.team_count.is_percent:
            team_count = self._ocr_result_count(frame.frame, frame.result.team_count)
            enemy_count = self._ocr_result_count(frame.frame, frame.result.enemy_count)
            is_percent = True
        else:
            team_count = self._ocr_result_percent(frame.frame, frame.result.team_count)
            enemy_count = self._ocr_result_percent(frame.frame, frame.result.enemy_count)
            is_percent = False

        indicator = BattleResult(
            team_count=team_count,
            enemy_count=enemy_count,
            is_percent=is_percent,
            win_lose=frame.result.win_lose
        )
        return BattleIndicatorAnalysisFrame(frame=frame.frame, rule=self.rule, nawabari_indicator=indicator)
    
    def _analyze_rest_count(self, frame: BattleIndicatorDetectionFrame, base_x: int) -> (int, int):
        team_count = None
        enemy_count = None
        for count in frame.indicator.counts:
            if count.xyxy[0] < base_x:
                team_count = count
            elif count.xyxy[0] > base_x:
                enemy_count = count
        if team_count is None or enemy_count is None:
            return None, None
        
        team_count_value = self._ocr_count_value(frame.frame, team_count)
        if team_count_value is None:
            return None, None
        enemy_count_value = self._ocr_count_value(frame.frame, enemy_count)
        if enemy_count_value is None:
            return None, None
        
        return team_count_value, enemy_count_value
     
    def _analyze_progress_count(self, frame: BattleIndicatorDetectionFrame) -> (int, int):
        team_count = None
        enemy_count = None
        if len(frame.indicator.counts) == 2:
            # counts are sorted with x
            team_count = self._ocr_count_value(frame.frame, frame.indicator.counts[1])
            enemy_count = self._ocr_count_value(frame.frame, frame.indicator.counts[0])
        elif len(frame.indicator.counts) == 1:
            # which theam does the count belong to 
            count = frame.indicator.counts[0]
            # determine by distance from timer
            if self.timer.xyxy[2] < count.xyxy[0]:
                team_count = self._ocr_count_value(frame.frame, count)
            elif count.xyxy[2] < self.timer.xyxy[0]:
                enemy_count = self._ocr_count_value(frame.frame, count)
            else:
                # determine by color of the count element
                img = self.reader.read(frame.frame)
                count_img = img[count.xyxy[1]:count.xyxy[3],count.xyxy[0]:count.xyxy[2]]
                side = InkColor.likely_side(count_img, self.team_color, self.enemy_color)
                if side == BattleSide.TEAM:
                    team_count = self._ocr_count_value(frame.frame, count)
                elif side == BattleSide.ENEMY:
                    enemy_count = self._ocr_count_value(frame.frame, count)

        return team_count, enemy_count
    
    def _analyze_penalty(self, frame: BattleIndicatorDetectionFrame, base_x: int) -> (int, int):
        team_penalty_value = None
        enemy_penalty_value = None
        for penalty in frame.indicator.penalties:
            if penalty.xyxy[0] < base_x:
                team_penalty_value = self._ocr_penalty_value(frame.frame, penalty)
            elif penalty.xyxy[0] > base_x:
                enemy_penalty_value = self._ocr_penalty_value(frame.frame, penalty)

        return team_penalty_value, enemy_penalty_value

    def _ocr_count_value(self, frame: int, count: DetectedItem) -> float:
        img = self.reader.read(frame)
        count_img = img[count.xyxy[1]:count.xyxy[3],count.xyxy[0]:count.xyxy[2]]
        lines = self.ocr.get_number_text(count_img, line_break=True)
        #cv2.imshow(s, count_img)
        #cv2.waitKey(0)
        try:
            return int(to_str(lines[1])) if len(lines) == 2 else None
        except:
            return None

    def _ocr_penalty_value(self, frame: int, penalty: DetectedItem) -> int:
        img = self.reader.read(frame)
        pena_img = img[penalty.xyxy[1]:penalty.xyxy[3],penalty.xyxy[0]:penalty.xyxy[2]]
        text = to_str(self.ocr.get_number_text(pena_img))
        text = text[1:] # remove '+' 
        try:
            return int(text) if 0 < len(text) and len(text) <= 2 else None 
        except:
            return None

    def _ocr_paint_point(self, frame: int, point: DetectedItem) -> int:
        img = self.reader.read(frame)
        point_img = img[point.xyxy[1]:point.xyxy[3],point.xyxy[0]:point.xyxy[2]]
        text = to_str(self.ocr.get_number_text(point_img))
        text = text[:-1] # remove 'p'
        try:
            return int(text) if 0 < len(text) and len(text) <= 4 else None
        except:
            return None

    def _ocr_value(self, frame, count: DetectedItem) -> int:
        img = self.reader.read(frame)
        count_img = img[count.xyxy[1]:count.xyxy[3],count.xyxy[0]:count.xyxy[2]]
        text = to_str(self.ocr.get_number_text(count_img))
        try:
            return int(text) if 0 < len(text) else None
        except:
            return None