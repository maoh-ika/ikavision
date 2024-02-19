from dataclasses import dataclass
from models.battle import BattleRule
from models.notification import NotificationType, Notification
from prediction.notification_detection_process import NotificationDetectionFrame, NotificationDetectionResult
from events.util import find_target_frames, TestResult

@dataclass
class BattleEndEvent:
    start_frame: int
    end_frame: int
    rule: BattleRule

class BattleEndEventCreator:
    def create(self, notif_result: NotificationDetectionResult) -> BattleEndEvent:
        notify_frames = notif_result.get_sliced_frames()
        start_idx, end_idx = find_target_frames(notify_frames, self._is_ending_frame, exit_test_frame_count=30)
        if start_idx is None:
            return None
        
        return BattleEndEvent(
            start_frame=notify_frames[start_idx].frame,
            end_frame=notify_frames[end_idx].frame,
            rule=BattleRule.UNKNOWN
        )

    def _is_ending_frame(self, frame: NotificationDetectionFrame, in_target_frame: bool) -> TestResult:
        end_notifs = list(filter(lambda n: n.type == NotificationType.NOTIFICATION_BATTLE_END, frame.notifications))
        return TestResult.TARGET if len(end_notifs) > 10 else TestResult.NOT_TARGET
