import time
import numpy as np
import Levenshtein
from error import INVALID_BATTLE_ERROR, InternalError
from events.battle_open_event import BattleOpenEvent
from events.battle_end_event import BattleEndEvent
from events.util import taget_frames_generator, TestResult
from prediction.notification_detection_process import NotificationDetectionResult
from prediction.ikalamp_detection_process import IkalampDetectionResult, IkalampDetectionFrame
from prediction.battle_indicator_detection_process import BattleIndicatorDetectionResult
from prediction.stage_frame_classifier import StageFrameClassifier
from prediction.buki_frame_classifier import BukiFrameClassifier
from prediction.weapon_gauge_frame_analyzer import WeaponGaugeFrameAnalyzer
from prediction.player_name_frame_analyzer import PlayerNameFrameAnalyzer
from prediction.splash_font_ocr import SplashFontOCR
from models.battle import BattleSide, BattleStage, BattleRule
from models.ika_player import IkaPlayer
from models.ikalamp import IkalampState
from models.ink_color import InkColor
from models.buki import Buki, SubWeapon, SpecialWeapon
from models.notification import NotificationType
from utils import choice_frames, normalized_levenshtein_distance, likely_value
from log import Logger

class BattleInfo:
    def __init__(self,
        battle_movie_path: str,
        movie_date: int,
        frame_rate: int,
        open_event: BattleOpenEvent,
        end_event: BattleEndEvent,
        notify_result: NotificationDetectionResult, 
        ikalamp_result: IkalampDetectionResult,
        ika_player_result: IkalampDetectionResult,
        indicator_result: BattleIndicatorDetectionResult,
        logger: Logger
    ) -> None:
        self.battle_movie_path = battle_movie_path
        self.movie_date = movie_date
        self.frame_rate = frame_rate
        self.open_event = open_event
        self.end_event = end_event

        self.notification = notify_result
        self.ikalamp = ikalamp_result
        self.ika_player = ika_player_result
        self.indicator = indicator_result

        self.logger = logger

    def build(self,
        stage_classifier: StageFrameClassifier,
        buki_classifier: BukiFrameClassifier,
        weapon_gauge_classifier: WeaponGaugeFrameAnalyzer,
        ocr: SplashFontOCR
    ) -> None:
        self.logger.info(f'stage process started.')
        processing_time = time.time()
        self.stage = self._predict_stage(stage_classifier)
        self.logger.info(f'stage process completed. processing time: {time.time() - processing_time}')
        
        self.logger.info(f'color process started.')
        processing_time = time.time()
        self.team_color, self.enemy_color = self._predict_color()
        self.logger.info(f'color process completed. processing time: {time.time() - processing_time}')

        self.logger.info(f'buki process started.')
        processing_time = time.time()
        self.team_bukis, self.enemy_bukis = self._predict_buki(buki_classifier)
        self.logger.info(f'buki process completed. processing time: {time.time() - processing_time}')

        self.logger.info(f'main player process started.')
        processing_time = time.time()
        self.main_player = self._find_main_player(weapon_gauge_classifier, ocr)
        self.logger.info(f'main player process completed. processing time: {time.time() - processing_time}')

    @property
    def battle_date(self):
        return self.movie_date + self.battle_open_frame // self.frame_rate
    
    @property
    def battle_open_frame(self):
        return self.open_event.start_frame if self.open_event else 0
    
    @property
    def battle_end_frame(self):
        return self.end_event.end_frame if self.end_event else -1
    
    @property
    def team_players(self):
        return self.open_event.team if self.open_event else []

    @property
    def enemy_players(self):
        return self.open_event.enemy if self.open_event else []
    
    @property
    def rule(self) -> BattleRule:
        return self.open_event.rule if self.open_event else BattleRule.UNKNOWN
    
    def get_player(self, side: BattleSide, ord: int) -> IkaPlayer:
        if self.open_event is None:
            return IkaPlayer('', '', '', side, ord)
        if side == BattleSide.TEAM:
            return self.open_event.team[ord]
        else:
            return self.open_event.enemy[ord]

    def find_player(self, name: str, side: BattleSide, conf_thresh: float=0) -> IkaPlayer:
        player_candidates = self.team_players if side == BattleSide.TEAM else self.enemy_players
        dists_norm = [normalized_levenshtein_distance(name, p.name) for p in player_candidates]
        dists = [Levenshtein.ratio(name, p.name) for p in player_candidates]
        min_idx = np.argmax(dists_norm)
        return player_candidates[min_idx] if dists[min_idx] > conf_thresh else None
        
    def find_likely_player(self, names: list[str], side: BattleSide, conf_thresh: float=0) -> IkaPlayer:
        players = [self.find_player(name, BattleSide.ENEMY, 0.2) for name in names]
        likely_ord = likely_value(players, lambda p: p.lamp_ord if p is not None else None)
        return self.get_player(BattleSide.ENEMY, likely_ord) if likely_ord is not None else None
        
    def _find_main_player(self, weapon_gauge_classifier: WeaponGaugeFrameAnalyzer, ocr: SplashFontOCR) -> IkaPlayer:
        # first, find ikalamp with the same sub-sp weapons pair
        lamp_frames = self.ikalamp.get_sliced_frames()
        test_lamp_frames = choice_frames(lamp_frames, 30, lambda f: f.team is not None)
        sub_weapon, sp_weapon = weapon_gauge_classifier.analyze_weapons(test_lamp_frames)
        same_weapons_ords = []
        if sub_weapon != SubWeapon.UNKNOWN and sp_weapon != SpecialWeapon.UNKNOWN:
            for ord, buki in enumerate(self.team_bukis):
                if buki.sub_weapon == sub_weapon and buki.sp_weapon == sp_weapon:
                    same_weapons_ords.append(ord)
            if len(same_weapons_ords) == 1:
                self.logger.info('main player found by sub-sp pair')
                return self.team_players[same_weapons_ords[0]]

        # second, if found two or more lamps, find lamp where the sp is fully charged at the same timing as weapon gauge
        if len(same_weapons_ords) >= 2:

            # gather ikalamp sp chaged frames
            sp_charged_frames = { ord: [] for ord in same_weapons_ords }
            for ord in same_weapons_ords:
                def _is_sp_frame(frame: IkalampDetectionFrame, in_target_frame: bool) -> TestResult:
                    if frame.team is None:
                        return TestResult.PENDING
                    return TestResult.TARGET if frame.team[ord].state == IkalampState.SP else TestResult.NOT_TARGET
   
                for sp_frames, _, _ in taget_frames_generator(lamp_frames, _is_sp_frame, 5):
                    if len(sp_frames) > 0:
                        sp_charged_frames[ord].append(sp_frames[0].frame)

            # gather weapon gauge sp chaged frames
            sp_gauge_frames = []
            is_gauge_charged = False
            for notif_frame in self.notification.get_sliced_frames():
                fullcharge_notifs = list(filter(lambda n: n.type == NotificationType.NOTIFICATION_SP_FULLCHARGE, notif_frame.notifications))
                if len(fullcharge_notifs) == 1:
                    if not is_gauge_charged:
                        sp_gauge_frames.append(notif_frame.frame)
                    is_gauge_charged = True
                else:
                    is_gauge_charged = False

            # count frames where both lamp and gauge are fully charged at the same timing
            sp_common_frame_count = { ord: 0 for ord in same_weapons_ords }
            for gauge_frame in sp_gauge_frames:
                for ord, frames in sp_charged_frames.items():
                    if len(list(filter(lambda f: gauge_frame - self.ikalamp.frame_interval <= f and f <= gauge_frame + self.ikalamp.frame_interval, frames))) == 1:
                        sp_common_frame_count[ord] += 1

            # The ord with the highest count of matching frames is the main player's
            sp_common_frame_count = list(sorted(sp_common_frame_count.items(), key=lambda x: x[1], reverse=True))
            if sp_common_frame_count[0][1] > sp_common_frame_count[1][1]:
                self.logger.info('main player found by sp charge timing')
                return self.team_players[sp_common_frame_count[0][0]]

        # third, find player whose name is not displayed in battle field
        if len(self.team_players) == 0 or self.team_color is None or self.enemy_color is None:
            return None
        
        first_lamp_frame = None
        for lamp in self.ikalamp.get_sliced_frames():
            if lamp.team and lamp.enemy:
                first_lamp_frame = lamp.frame
                break

        ika_player_copy = self.ika_player.slice(first_lamp_frame)
        ika_frames = ika_player_copy.get_sliced_frames()
        
        player_name_analyzer = PlayerNameFrameAnalyzer(
            battle_movie_path=self.battle_movie_path,
            team_players=self.team_players,
            enemy_players=[],
            team_color=self.team_color,
            enemy_color=self.enemy_color,
            ocr=ocr
        )
        
        players = self.team_players.copy()
        if len(same_weapons_ords) > 0:
            players = list(filter(lambda p: p.lamp_ord in same_weapons_ords, players)) # ignore players who did not pass tests up to here
        for i in range(0, len(ika_frames), 100):
            frames = ika_frames[i: i + 100]
            result = player_name_analyzer.analyze(frames)
            for name_frame in result.frames:
                for name_player in name_frame.players:
                    players = list(filter(lambda p: p.lamp_ord != name_player.player.lamp_ord, players))
                    if len(players) == 1:
                        self.logger.info('main player found by player names')
                        return players[0]
                    
        return None
    
    def _predict_stage(self, stage_classifier: StageFrameClassifier) -> BattleStage:
        battle_frames = self.notification.get_sliced_frames()
        retry_count = len(battle_frames) // 200
        while retry_count > 0:
            test_frames = choice_frames(battle_frames, 100)
            stage = stage_classifier.classify(test_frames)
            if stage is not None:
                return stage
            retry_count -=1
        
        raise INVALID_BATTLE_ERROR
    
    def _predict_color(self) -> (InkColor, InkColor):
        frames = self.ikalamp.get_sliced_frames()
        retry_count = len(frames) // 30
        while retry_count > 0:
            test_frames = choice_frames(frames, 30)
            team_color = InkColor.create_from_ikalamp(self.battle_movie_path, test_frames, BattleSide.TEAM)
            enemy_color = InkColor.create_from_ikalamp(self.battle_movie_path, test_frames, BattleSide.ENEMY)
            if team_color is not None and enemy_color is not None:
                return team_color, enemy_color
            retry_count -=1
        
        raise InternalError('color prediction failed')
    
    def _predict_buki(self, buki_classifier: BukiFrameClassifier) -> (list[Buki], list[Buki]):
        battle_frames = self.ikalamp.get_sliced_frames()
        if len(battle_frames) == 0:
            return BattleStage.UNKNOWN
        test_count = 30 if self.rule != BattleRule.HOKO else 60
        test_frames = choice_frames(battle_frames, test_count, lambda f: f.team is not None)
        (team_mains, enemy_mains) = buki_classifier.classify_most_likely(test_frames)
        team_bukis = [Buki.create(main, self.battle_date) for main in team_mains] 
        enemy_bukis = [Buki.create(main, self.battle_date) for main in enemy_mains]
        return (team_bukis, enemy_bukis)