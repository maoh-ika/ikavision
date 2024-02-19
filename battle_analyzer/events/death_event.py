from dataclasses import dataclass
from enum import Enum
from threading import Thread
import numpy as np
import Levenshtein
from models.ika_player import IkaPlayer
from models.ikalamp import IkalampState
from models.battle import BattleSide
from models.battle_info import BattleInfo
from models.notification import NotificationType, Notification
from models.text import to_str, likely_text
from prediction.ikalamp_detection_process import IkalampDetectionResult, IkalampDetectionFrame
from prediction.notification_detection_process import NotificationDetectionResult, NotificationDetectionFrame
from prediction.splash_font_ocr import SplashFontOCR
from prediction.plate_frame_analyzer import PlateFrameAnalyzer
from utils import MovieReader
from events.util import taget_frames_generator, TestResult
from error import InternalError

class DeathReasonType(Enum):
    MAIN_WEAPON = 0
    SUB_WEAPON = 1
    SP_WEAPON = 2
    HOKO_SHOOT = 3
    OTHER = 4
    UNKNOWN = 99

@dataclass
class DeathEvent:
    death_player: IkaPlayer
    kill_player: IkaPlayer
    death_reason: str
    reason_type: DeathReasonType
    start_frame: int
    end_frame: int

@dataclass
class DeathNotification:
    death_reason: str
    reason_type: DeathReasonType
    kill_player: IkaPlayer
    start_frame: int
    end_frame: int

class DeathMonitor:
    def __init__(self, side: BattleSide, ord: int, drop_frame_start: int=None) -> None:
        self.side = side
        self.ord = ord
        self.drop_frame_start = drop_frame_start
        self.drop_frame_false_range = 30

    def is_death_frame(self, frame: IkalampDetectionFrame, in_target_frame: bool) -> TestResult:
        if (self.side == BattleSide.TEAM and frame.team is None) or (self.side == BattleSide.ENEMY and frame.enemy is None):
            return TestResult.TARGET if in_target_frame else TestResult.NOT_TARGET # assume that death frame continues until non-death frames found
        
        if self.drop_frame_start and self.drop_frame_start - self.drop_frame_false_range <= frame.frame:
            return TestResult.NOT_TARGET

        lamp = frame.team[self.ord] if self.side == BattleSide.TEAM else frame.enemy[self.ord]
        return TestResult.TARGET if lamp.state == IkalampState.DEATH else TestResult.NOT_TARGET


class DeathEventCreator(Thread):
    def __init__(self,
        battle_info: BattleInfo,
        ocr: SplashFontOCR,
        plate_analyzer: PlateFrameAnalyzer) -> None:
        super().__init__(name='DeathEventCreator')
        self.battle_info = battle_info
        self.ocr = ocr
        self.plate_analyzer = plate_analyzer
        self.last_frame = None
        self.reader = MovieReader(self.battle_info.battle_movie_path)
        self.ikalamp_result: IkalampDetectionResult = None
        self.notif_result: NotificationDetectionResult = None
        self.events: list[DeathEvent] = None

    def create(self,
        ikalamp_result: IkalampDetectionResult,
        notif_result: NotificationDetectionResult
    ) -> list[DeathEvent]:
       self.ikalamp_result = ikalamp_result
       self.notif_result = notif_result
       self.start() 

    def run(self):
        if self.ikalamp_result is None or self.notif_result is None:
            raise InternalError('run must be called via create')
        death_notifications = self._detect_death_notifications(self.notif_result)
        
        ikalamp_frames = self.ikalamp_result.slice(self.ikalamp_result.start_frame, self.battle_info.end_event.start_frame).get_sliced_frames()
        players = self.battle_info.team_players + self.battle_info.enemy_players
        events = []
        for player in players:
            monitor = DeathMonitor(player.side, player.lamp_ord, self._find_drop_frame(player))
            generator = taget_frames_generator(ikalamp_frames, monitor.is_death_frame, exit_test_frame_count=2)
            for death_frames, _, _ in generator:
                if len(death_frames) < 2: # at least two consecutive frames
                    continue
                        
                events.append(self._make_death_event(
                    player,
                    death_frames[0].frame,
                    death_frames[-1].frame,
                    death_notifications
                ))

        self.events = events

    def _detect_death_notifications(self, notif_result: NotificationDetectionResult) -> list[DeathNotification]:
        main_deaths = []
        notif_frames = notif_result.get_sliced_frames()
        
        generator = taget_frames_generator(notif_frames, self._is_death_frame, exit_test_frame_count=30)
        for death_frames, _, _ in generator:
            start_frame = death_frames[0].frame
            end_frame = death_frames[-1].frame
            death_reason_texts = []
            kill_player_names = []
            for death_frame in death_frames:
                reason_notif = self._get_reason_notifs(death_frame)
                plate_notif = self._get_plate_notifs(death_frame)
                if len(reason_notif) != 1 or len(plate_notif) != 1:
                    continue
                
                reason_text = self._detect_death_reason(reason_notif[0], death_frame.frame)
                if reason_text != '':
                    death_reason_texts.append(reason_text)

                killer_name = self._detect_killer_name(death_frame)
                if killer_name != '':
                    kill_player_names.append(killer_name)

            reason_text_likely = likely_text(death_reason_texts)
            kill_player = self.battle_info.find_likely_player(kill_player_names, BattleSide.ENEMY, 0.3)
            main_death = self._make_death_notification(
                reason_text_likely,
                kill_player,
                start_frame,
                end_frame
            )
            if main_death:
                main_deaths.append(main_death)
        
        return main_deaths
    
    def _is_death_frame(self, frame: NotificationDetectionFrame, in_target_frame: bool) -> TestResult:
        reason_count = len(self._get_reason_notifs(frame))
        killer_count = len(self._get_plate_notifs(frame))
        gear_count = len(self._get_gear_notifs(frame))
        return TestResult.TARGET if reason_count == 1 and killer_count == 1 and gear_count == 1 else TestResult.NOT_TARGET
    
    def _get_reason_notifs(self, frame: NotificationDetectionFrame) -> list[Notification]:
        return list(filter(lambda n: n.type == NotificationType.NOTIFICATION_DEATH_REASON, frame.notifications))
    
    def _get_plate_notifs(self, frame: NotificationDetectionFrame) -> list[Notification]:
        return list(filter(lambda n: n.type == NotificationType.NOTIFICATION_PLAYER_PLATE, frame.notifications))
    
    def _get_gear_notifs(self, frame: NotificationDetectionFrame) -> list[Notification]:
        return list(filter(lambda n: n.type == NotificationType.NOTIFICATION_PLAYER_GEAR, frame.notifications))

    def _detect_death_reason(self, reason_notif: Notification, frame_number: int) -> str:
        img = self.reader.read(frame_number)
        reason_img = img[reason_notif.xyxy[1]:reason_notif.xyxy[3],reason_notif.xyxy[0]:reason_notif.xyxy[2]]
        lines = self.ocr.get_text(reason_img, line_break=True)
        lines = list(filter(lambda l: len(l) >= 4, lines))
        if len(lines) < 2:
            return ''
        reason_line = to_str(lines[-2]) # reason is in the second line from the bottom
        if reason_line.endswith(('で', 'て')):
            reason_line = reason_line[:-2]
        return reason_line
    
    def _detect_killer_name(self, frame: NotificationDetectionFrame) -> str:
        plate_result = self.plate_analyzer.analyze([frame], ignore_nickname=True, ignore_id=True, ignore_badge=True)
        if len(plate_result.frames[0].plates) == 0:
            return ''
        plate = plate_result.frames[0].plates[0]
        return plate.player_name.text if plate.player_name is not None else ''
    
    def _make_death_notification(self,
        reason_text: str,
        kill_player: IkaPlayer,
        start_frame: int,
        end_frame: int) -> DeathNotification:
        if kill_player is None:
            return None
        if len(self.battle_info.enemy_bukis) <= kill_player.lamp_ord:
            return None
        kill_buki = self.battle_info.enemy_bukis[kill_player.lamp_ord]

        reason_candidates = [
            kill_buki.main_label,
            kill_buki.sub_label,
            kill_buki.sp_label,
            'ホコショット' # Japanease only
        ]
        dists = [Levenshtein.ratio(reason_text, candidate) for candidate in reason_candidates]
        min_idx = np.argmax(dists)
        reason_idx = min_idx if dists[min_idx] > 0.3 else None

        if reason_idx == 0:
            reason_type = DeathReasonType.MAIN_WEAPON
            reason = kill_buki.main_id
        elif reason_idx == 1:
            reason_type = DeathReasonType.SUB_WEAPON
            reason = kill_buki.sub_id
        elif reason_idx == 2:
            reason_type = DeathReasonType.SP_WEAPON
            reason = kill_buki.sp_id
        elif reason_idx == 3:
            reason_type = DeathReasonType.HOKO_SHOOT
            reason = 'hoko_shoot'
        else:
            reason_type = DeathReasonType.OTHER
            reason = reason_text

        return DeathNotification(
            death_reason=reason,
            reason_type=reason_type,
            kill_player=kill_player,
            start_frame=start_frame,
            end_frame=end_frame
        )

    def _make_death_event(self,
        death_player: IkaPlayer,
        start_frame: int,
        end_frame: int,
        death_notifications: list[DeathNotification] 
     ) -> DeathEvent:
        is_enemy = death_player.side == BattleSide.ENEMY
        is_not_main_player = self.battle_info.main_player is None or death_player.lamp_ord != self.battle_info.main_player.lamp_ord
        match_death = list(filter(lambda death: death.end_frame >= start_frame and death.start_frame <= end_frame, death_notifications))
        if is_enemy or is_not_main_player or len(match_death) == 0:
            return DeathEvent(
                death_player=death_player,
                kill_player=None,
                death_reason='',
                reason_type=DeathReasonType.UNKNOWN,
                start_frame=start_frame,
                end_frame=end_frame
            )
        else:
            return DeathEvent(
                death_player=death_player,
                kill_player=match_death[0].kill_player,
                death_reason=match_death[0].death_reason,
                reason_type=match_death[0].reason_type,
                start_frame=start_frame,
                end_frame=end_frame
            )
        
    def _find_drop_frame(self, player: IkaPlayer) -> int:
        def _is_drop_frame(frame: IkalampDetectionFrame, in_target_frame: bool) -> TestResult:
            if (player.side == BattleSide.TEAM and frame.team is None) or (player.side == BattleSide.ENEMY and frame.enemy is None):
                return TestResult.PENDING
            lamp = frame.team[player.lamp_ord] if player.side == BattleSide.TEAM else frame.enemy[player.lamp_ord]
            return TestResult.TARGET if lamp.state == IkalampState.DROP else TestResult.NOT_TARGET
        
        generator = taget_frames_generator(self.ikalamp_result.frames, _is_drop_frame, exit_test_frame_count=30)
        for drop_frames, _, _ in generator:
            if len(drop_frames) > 10:
                return drop_frames[0].frame

        return None