from dataclasses import dataclass
import numpy as np
from models.ika_player import IkaPlayer
from models.battle import BattleSide
from models.battle_info import BattleInfo
from models.notification import NotificationType, Notification
from models.text import to_str, likely_text
from prediction.notification_detection_process import NotificationDetectionResult, NotificationDetectionFrame
from prediction.splash_font_ocr import SplashFontOCR
from utils import MovieReader
from events.util import taget_frames_generator, TestResult

@dataclass
class InkInsufficientEvent:
    start_frame: int
    end_frame: int

class InkInsufficientEventCreator:
    def __init__(self, battle_info: BattleInfo) -> None:
        self.battle_info = battle_info

    def create(self, notif_result: NotificationDetectionResult) -> list[InkInsufficientEvent]:
        events = []
        notif_frames = notif_result.get_sliced_frames()

        generator = taget_frames_generator(notif_frames, self._is_kill_frame, exit_test_frame_count=30)
        for kill_frames, _, _ in generator:
            start_frame = kill_frames[0].frame
            end_frame = kill_frames[-1].frame
            if end_frame - start_frame < 60:
                continue
        
        return events
    
    def _is_kill_frame(self, frame: NotificationDetectionFrame, in_target_frame: bool) -> TestResult:
        kill_notif = list(filter(lambda n: n.type == NotificationType.NOTIFICATION_KILL, frame.notifications))
        return TestResult.TARGET if len(kill_notif) == 1 else TestResult.NOT_TARGET
    