from dataclasses import dataclass
from threading import Thread
import Levenshtein
from models.ika_player import IkaPlayer
from models.battle import BattleSide
from models.battle_info import BattleInfo
from models.notification import NotificationType, Notification
from models.text import to_str
from models.ikalamp import IkalampState
from prediction.notification_detection_process import NotificationDetectionResult, NotificationDetectionFrame
from prediction.ikalamp_detection_process import IkalampDetectionResult
from prediction.splash_font_ocr import SplashFontOCR
from utils import MovieReader, find_one, likely_value
from events.util import taget_frames_generator, TestResult
from error import InternalError

@dataclass
class KillEvent:
    kill_player: IkaPlayer
    death_player: IkaPlayer
    start_frame: int
    end_frame: int

class KillEventCreator(Thread):
    def __init__(self,
        battle_info: BattleInfo,
        ocr: SplashFontOCR) -> None:
        super().__init__(name='KillEventCreator')
        self.battle_info = battle_info
        self.ocr = ocr
        self.reader = MovieReader(self.battle_info.battle_movie_path)
        self.notif_result: NotificationDetectionResult = None
        self.ikalamp_result: IkalampDetectionResult = None
        self.events: list[KillEvent] = None

    def create(self, notif_result: NotificationDetectionResult, ikalamp_result: IkalampDetectionResult) -> list[KillEvent]:
        self.notif_result = notif_result
        self.ikalamp_result = ikalamp_result
        self.start()
    
    def run(self) -> list[KillEvent]:
        if self.notif_result is None or self.ikalamp_result is None:
            raise InternalError('run must be called via create')
        events = []
        notif_frames = self.notif_result.get_sliced_frames()

        generator = taget_frames_generator(notif_frames, self._is_kill_frame, exit_test_frame_count=5)
        for kill_frames, _, _ in generator:
            if len(kill_frames) == 0:
                continue
            
            # gather death player names with same track id
            death_player_name_frames = []
            for kill_frame in kill_frames:
                kill_notifs = list(filter(lambda n: n.type == NotificationType.NOTIFICATION_KILL, kill_frame.notifications))
                for kill_notif in kill_notifs:
                    death_player_name = self._detect_death_player_name(kill_notif, kill_frame.frame)
                    if death_player_name != '':
                        death_player_name_frames.append((death_player_name, kill_frame.frame))

            # merge death player names which are tied to same player even though diffrent track id 
            evt_candidates = []
            left_death_player_name_frames = death_player_name_frames.copy()
            left_death_player_name_frames.sort(key=lambda i: i[0]) # sort by name
            while len(left_death_player_name_frames) > 0:
                death_player_names = list(map(lambda nf: nf[0], left_death_player_name_frames))
                death_player = self.battle_info.find_likely_player(death_player_names, BattleSide.ENEMY, 0.3)
                if death_player is None:
                    break
                # remove other player names dead at the same time.
                likely_death_player_name_frames = self._find_likely_frames(left_death_player_name_frames, death_player.name)
                likely_death_player_name_frames.sort(key=lambda i: i[1]) # sort by frame
                start_frame = likely_death_player_name_frames[0][1]
                end_frame = likely_death_player_name_frames[-1][1]
                
                left_death_player_name_frames = [nf for nf in left_death_player_name_frames if nf not in likely_death_player_name_frames]

                if not self._is_player_dead(death_player, start_frame, end_frame):
                    break

                if death_player is not None:
                    existing_evt = list(filter(lambda e: e.death_player == death_player, evt_candidates))
                    if len(existing_evt) == 0:
                        event = KillEvent(
                            kill_player=self.battle_info.main_player,
                            death_player=death_player,
                            start_frame=start_frame,
                            end_frame=end_frame
                        )
                        evt_candidates.append(event)

            # fix event frame range
            sorted_items = sorted(death_player_name_frames, key=lambda i: i[1])
            for evt in evt_candidates:
                items = self._find_likely_frames(sorted_items, evt.death_player.name)
                evt.start_frame = min(evt.start_frame, items[0][1])
                evt.end_frame = max(evt.end_frame, items[-1][1])
            
            events += evt_candidates
        
        self.events = events
    
    def _is_kill_frame(self, frame: NotificationDetectionFrame, in_target_frame: bool) -> TestResult:
        kill_notif = list(filter(lambda n: n.type == NotificationType.NOTIFICATION_KILL, frame.notifications))
        return TestResult.TARGET if len(kill_notif) >= 1 else TestResult.NOT_TARGET
    
    def _detect_death_player_name(self, kill_notif: Notification, frame_number: int) -> str:
        if kill_notif.conf < 0.8:
            return ''
        img = self.reader.read(frame_number)
        kill_img = img[kill_notif.xyxy[1]:kill_notif.xyxy[3],kill_notif.xyxy[0]:kill_notif.xyxy[2]]
        kill_text = self.ocr.get_text(kill_img)
        if len(kill_text) == 0:
            return ''
        first = kill_text[0]
        if first.xyxy[0] < first.width: # did kill icon detected as char ?
            kill_text = kill_text[1:] # remove kill icon
        sufix_text = to_str(kill_text[-6:])
        sufix_expected = 'をたおした。' # Japanease only
        sufix_ratio = Levenshtein.ratio(sufix_text, sufix_expected)
        if sufix_ratio < 0.5:
            return ''
        kill_text = kill_text[:-6] # remove sufix
        return to_str(kill_text)
    
    def _find_likely_frames(self, name_frames: list[(str, int)], target: str) -> list[(str, int)]:
        if len(name_frames) == 0:
            raise Exception('invalid array')
        
        res = []
        for name_frame in name_frames:
            p = self.battle_info.find_player(name_frame[0], BattleSide.ENEMY, 0.2)
            if p is not None and p.name == target:
                res.append(name_frame)

        return res

    def _is_player_dead(self, player: IkaPlayer, start_frame: int, end_frame: int) -> bool:
        ikalamp = self.ikalamp_result.slice(start_frame, end_frame)
        for ikalamp in ikalamp.get_sliced_frames():
            if player.side == BattleSide.TEAM and ikalamp.team is not None:
                if ikalamp.team[player.lamp_ord].state == IkalampState.DEATH:
                    return True
            elif player.side == BattleSide.ENEMY and ikalamp.enemy is not None:
                if ikalamp.enemy[player.lamp_ord].state == IkalampState.DEATH:
                    return True
        return False