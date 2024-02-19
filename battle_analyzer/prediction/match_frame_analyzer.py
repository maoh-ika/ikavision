from dataclasses import dataclass
from threading import Thread
import numpy as np
import Levenshtein
from error import InternalError
from models.battle import MatchType
from models.detected_item import DetectedItem
from models.text import to_str
from prediction.notification_detection_process import NotificationDetectionResult
from prediction.match_detection_process import MatchDetectionResult, MatchDetectionFrame, run_match_detection
from prediction.splash_font_ocr import SplashFontOCR
from events.battle_open_event import BattleOpenEvent, BattleOpenEventCreator
from events.battle_result_event import BattleResultEvent
from utils import MovieReader, likely_value

@dataclass
class MatchAnalysisResult:
    match_type: MatchType
    match_rate: float
    match_rate_updated: float

class MatchFrameAnalyzer(Thread):
    def __init__(self,
        battle_movie_path: str,
        match_model_path: str,
        device: str,
        process_id: int,
        ocr: SplashFontOCR) -> None:
        super().__init__()
        self.match_model_path = match_model_path
        self.device = device
        self.process_id = process_id
        self.ocr = ocr
        self.reader = MovieReader(battle_movie_path)
        self.notif_result: NotificationDetectionResult = None
        self.open_event: BattleOpenEvent = None
        self.result_event: BattleResultEvent = None
        self.prev_open_event: BattleOpenEvent = None
        self.prev_match: MatchAnalysisResult = None
        self.result: MatchAnalysisResult = None

    def analyze(self,
        notif_result: NotificationDetectionResult,
        open_event: BattleOpenEvent,
        result_event: BattleResultEvent,
        prev_open_event: BattleOpenEvent,
        prev_match: MatchAnalysisResult
    ) -> MatchAnalysisResult:
        self.notif_result = notif_result
        self.open_event = open_event
        self.result_event = result_event
        self.prev_open_event = prev_open_event
        self.prev_match = prev_match
        self.start()
        
    def run(self):
        match_candidates = []
        match_rate_update_before = None
        match_rate_updated_after = None
        match_rate_menu_value = None

        next_notif_result = self.notif_result.slice(self.result_event.end_frame)
        next_open_event = BattleOpenEventCreator(0).create(next_notif_result, None, None, player_detection_enabled=False)
        next_open_frame = next_open_event.start_frame if next_open_event else None
        target_match_frames = self.detect_match_frames(self.result_event.end_frame, next_open_frame)
        prev_match_frames = []
        if self.prev_open_event is None:
            # no battle before, so include frames from movie start to the battle open
            prev_match_frames = self.detect_match_frames(0, self.open_event.start_frame)

        for frame in prev_match_frames:
            if frame.match_rate_item_menu_x:
                img = self.reader.read(frame.frame)
                rate = self.parse_x_rate_menu(frame.match_rate_item_menu_x, img)
                if rate is not None and rate < 10000:
                    if match_rate_menu_value is None:
                        match_rate_menu_value = rate
                        break

        for frame in target_match_frames:
            if frame.match_type_item:
                img = self.reader.read(frame.frame)
                match_type = self.parse_match_type(frame.match_type_item, img)
                if match_type != MatchType.UNKNOWN:
                    match_candidates.append(match_type)
            if frame.match_rate_item_update_x:
                img = self.reader.read(frame.frame)
                rate = self.parse_x_rate_update(frame.match_rate_item_update_x, img)
                if rate is not None and rate < 10000:
                    if match_rate_update_before is None: # the value before update is the xp for the battle
                        match_rate_update_before = rate
                    match_rate_updated_after = rate
            if match_rate_menu_value is None and frame.match_rate_item_menu_x:
                img = self.reader.read(frame.frame)
                rate = self.parse_x_rate_menu(frame.match_rate_item_menu_x, img)
                if rate is not None and rate < 10000:
                    if match_rate_menu_value is None:
                        match_rate_menu_value = rate
        
        likely_match_type = MatchType.UNKNOWN
        if len(match_candidates) > 0:
            likely_match_type = likely_value(match_candidates)

        likely_match_rate = None
        likely_match_rate_updated = None
        if likely_match_type == MatchType.X_MATCH:
            if match_rate_update_before is not None:
                # use value from xp update 
                likely_match_rate = match_rate_update_before
                likely_match_rate_updated = match_rate_updated_after
            else: # no xp update
                if match_rate_menu_value is not None:
                    likely_match_rate = match_rate_menu_value
                    likely_match_rate_updated = match_rate_menu_value
                else:
                    if self.prev_match and self.prev_match.match_type == likely_match_type and self.prev_open_event.rule == self.open_event.rule:
                        # same match type and rule, reuse prev updated xp
                        likely_match_rate = self.prev_match.match_rate_updated
                        likely_match_rate_updated = self.prev_match.match_rate_updated

        self.result = MatchAnalysisResult(
            match_type=likely_match_type,
            match_rate=likely_match_rate,
            match_rate_updated=likely_match_rate_updated
        )

    def parse_x_rate_update(self, item: DetectedItem, img: np.ndarray) -> float:
        rate_img = img[item.xyxy[1]:item.xyxy[3],item.xyxy[0]:item.xyxy[2]]
        lines = self.ocr.get_number_text(rate_img, line_break=True)
        try:
            return float(to_str(lines[1])) if len(lines) == 2 else None
        except:
            return None

    def parse_x_rate_menu(self, item: DetectedItem, img: np.ndarray) -> float:
        rate_img = img[item.xyxy[1]:item.xyxy[3],item.xyxy[0]:item.xyxy[2]]
        symbols = self.ocr.get_symbol_text(rate_img)
        numbers = self.ocr.get_number_text(rate_img)
        if len(symbols) != len(numbers):
            return None
        for i in range(len(symbols)):
            if symbols[i].value == '-': # find the position of '-' of 'Xパワー：'
                rate = to_str(numbers[i + 2:])
                try:
                    return float(rate)
                except:
                    return None
        return None
    
    def parse_match_type(self, item: DetectedItem, img: np.ndarray) -> MatchType:
        type_img = img[item.xyxy[1]:item.xyxy[3],item.xyxy[0]:item.xyxy[2]]
        type_text = to_str(self.ocr.get_text(type_img))

        # Japanease only 
        type_candidates = [
            { 'label': 'レギュラーマッチ', 'type': MatchType.REGULAR_MATCH },
            { 'label': 'バンカラマッチ', 'type': MatchType.BANKARA_MATCH },
            { 'label': 'Xマッチ', 'type': MatchType.X_MATCH },
            { 'label': 'イベントマッチ', 'type': MatchType.EVENT_MATCH },
            { 'label': 'フェスマッチ', 'type': MatchType.FES_MATCH },
            { 'label': 'プライベートマッチ', 'type': MatchType.PRIV_MATCH }
        ]
        dists = [Levenshtein.ratio(type_text, candidate['label']) for candidate in type_candidates]
        min_idx = np.argmax(dists)
        return type_candidates[np.argmax(dists)]['type'] if dists[min_idx] > 0.3 else MatchType.UNKNOWN

    def detect_match_frames(self, start_frame: int, end_frame: int) -> list[MatchDetectionFrame]:  
        result = run_match_detection(
            battle_movie_path=self.reader.movie_path,
            match_model_path=self.match_model_path,
            frame_interval=3,
            device=self.device,
            process_id=self.process_id,
            batch_size=10,
            start_frame=start_frame,
            end_frame=end_frame,
            write_shared_memory=False
        )
        if result is None:
            raise InternalError('match detection failed')
        return result.frames
