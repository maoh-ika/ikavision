from dataclasses import dataclass
from multiprocessing import Process, Value
import time
import os
import multiprocessing
import cv2
import torch
from version import SPLATOON_VERSION
from error import *
from log import Logger 
from prediction.ikalamp_detection_process import run_ikalamp_detection, SharedIkalampDetectionResult, IkalampDetectionResult
from prediction.ika_player_detection_process import run_ika_player_detection, SharedIkaPlayerDetectionResult, IkaPlayerDetectionResult
from prediction.notification_detection_process import run_notification_detection, SharedNotificationDetectionResult, NotificationDetectionResult
from prediction.battle_indicator_detection_process import run_battle_indicator_detection, SharedBattleIndicatorDetectionResult, BattleIndicatorDetectionResult
from prediction.match_detection_process import run_match_detection, SharedMatchDetectionResult, MatchDetectionResult 
from prediction.splash_font_ocr import SplashFontOCR
from prediction.plate_frame_analyzer import PlateFrameAnalyzer
from prediction.stage_frame_classifier import StageFrameClassifier
from prediction.buki_frame_classifier import BukiFrameClassifier
from prediction.sub_weapon_frame_classifier import SubWeaponFrameClassifier
from prediction.special_weapon_frame_classifier import SpecialWeaponFrameClassifier
from prediction.weapon_gauge_frame_analyzer import WeaponGaugeFrameAnalyzer
from prediction.player_position_frame_analyzer import PlayerPositionFrameAnalyzer, PlayerPositionAnalysisResult
from prediction.ink_tank_frame_analyzer import InkTankFrameAnalyzer, InkTankAnalysisResult
from prediction.battle_indicator_frame_analyzer import BattleIndicatorFrameAnalyzer
from prediction.match_frame_analyzer import MatchFrameAnalyzer, MatchAnalysisResult
from models.battle import BattleRule
from models.battle_info import BattleInfo
from events.battle_open_event import BattleOpenEventCreator
from events.battle_end_event import BattleEndEventCreator
from events.battle_result_event import BattleResultEventCreator, BattleResultEvent
from events.death_event import DeathEventCreator, DeathEvent
from events.kill_event import KillEventCreator, KillEvent
from events.player_number_balance_event import PlayerNumberBalanceEventCreator, PlayerNumberBalanceEvent
from events.battle_countdown_event import BattleCountEventCreator, BattleCountEvent
from events.special_weapon_event import SpecialWeaponEventCreator, SpecialWeaponEvent

@dataclass
class ModelPaths:
    ikalamp_model_path: str
    ika_player_model_path: str
    notification_model_path: str
    match_model_path: str
    plate_model_path: str
    battle_indicator_model_path: str
    char_type_model_path: str
    hiragana_model_path : str
    katakana_model_path : str
    number_model_path : str
    alphabet_model_path : str
    symbol_model_path : str
    char_model_path : str
    stage_model_path : str
    buki_model_path : str
    sub_weapon_model_path : str
    sp_weapon_model_path : str
    weapon_gauge_model_path: str
    ink_tank_model_path : str

@dataclass
class BattlePreprocessParams:
    battle_movie_path: str
    movie_date: int = int(time.time())
    start_frame: int = 0
    end_frame: int = None
    analysis_per_second: int = 10
    process_id: int = 0
    batch_size: int = 1

@dataclass
class BattlePreprocessResult:
    movie_width: int
    movie_height: int
    movie_frames: int
    frame_rate: int

@dataclass
class BattleAnalysisParams:
    start_frame: int = 0
    end_frame: int = None

@dataclass
class BattleAnalysisResult:
    version: str
    battle_frames: int
    battle_info: BattleInfo
    result_event: BattleResultEvent
    kill_events: list[KillEvent]
    death_events: list[DeathEvent]
    team_count_events: list[BattleCountEvent]
    enemy_count_events: list[BattleCountEvent]
    player_number_balance_events: list[PlayerNumberBalanceEvent]
    special_weapon_events: list[SpecialWeaponEvent]
    position_result: PlayerPositionAnalysisResult
    ink_tank_result: InkTankAnalysisResult
    match_info: MatchAnalysisResult

def init():
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass

class BattleAnalyzer:
    def __init__(self,
        model_paths: ModelPaths,
        device: str,
        log_name: str
    ) -> None:
        self.model_paths = model_paths
        self.device = device
        self.logger = Logger(log_name)
        self.preprocess_params: BattlePreprocessParams = None
        self.ikalamp_result: IkalampDetectionResult = None
        self.ika_player_result: IkaPlayerDetectionResult = None
        self.notification_result: NotificationDetectionResult = None
        self.indicator_result: BattleIndicatorDetectionResult = None
        self.frame_rate = None
        self.frame_interval = None
        self.prev_result: BattleAnalysisResult = None

    def preprocess(self, params: BattlePreprocessParams) -> None:
        if not os.path.exists(params.battle_movie_path):
            raise INVALID_PARAMS_ERROR
        
        self.preprocess_params = params

        try:
            SharedIkalampDetectionResult.set_id(params.process_id)
            SharedIkalampDetectionResult.reset()
            SharedIkaPlayerDetectionResult.set_id(params.process_id)
            SharedIkaPlayerDetectionResult.reset()
            SharedNotificationDetectionResult.set_id(params.process_id)
            SharedNotificationDetectionResult.reset()
            SharedBattleIndicatorDetectionResult.set_id(params.process_id)
            SharedBattleIndicatorDetectionResult.reset()
            
            cap = cv2.VideoCapture(self.preprocess_params.battle_movie_path)
            self.frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            analysis_per_second = self.preprocess_params.analysis_per_second or self.frame_rate
            self.frame_interval = int(self.frame_rate / analysis_per_second)

            notification_detecotr = self._create_notification_process(self.frame_interval, self.preprocess_params.batch_size, 0, None)
            notification_detecotr.start()
            notification_detecotr.join()
            self.notification_result = SharedNotificationDetectionResult.read()
            
            if self.notification_result is None:
                raise InternalError('prepress frames failed')
            
            self.logger.info(f'notification process completed. processing time: {self.notification_result.processing_time}')
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            return BattlePreprocessResult(
                movie_width=width,
                movie_height=height,
                movie_frames=frame_count,
                frame_rate=self.frame_rate
            )
        except InternalError as e:
            raise e
        except Exception as e:
            raise InternalError(str(e))

    def analyze(self, params: BattleAnalysisParams) -> (BattleAnalysisResult, ErrorCode):
        if self.preprocess_params is None:
            raise IndentationError('preprocess must be invoked before analysis')
        
        self.logger.info(f'analysis started. frame {params.start_frame} to {params.end_frame}')

        # create analysis stuffs
        ocr = self._create_ocr()
        plate_analyzer = PlateFrameAnalyzer(
            plate_model_path=self.model_paths.plate_model_path,
            battle_movie_path=self.preprocess_params.battle_movie_path,
            device=self.device,
            ocr=ocr
        )

        stage_classifier = StageFrameClassifier(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            model_path=self.model_paths.stage_model_path,
            device=self.device
        )
        
        buki_classifier = BukiFrameClassifier(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            model_path=self.model_paths.buki_model_path,
            device=self.device
        )
        
        sub_weapon_classifier = SubWeaponFrameClassifier(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            model_path=self.model_paths.sub_weapon_model_path,
            device=self.device
        )
        
        sp_weapon_classifier = SpecialWeaponFrameClassifier(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            model_path=self.model_paths.sp_weapon_model_path,
            device=self.device
        )

        weapon_gauge_analyzer = WeaponGaugeFrameAnalyzer(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            weapon_gauge_model_path=self.model_paths.weapon_gauge_model_path,
            sub_weapon_classifier=sub_weapon_classifier,
            sp_weapon_classifier=sp_weapon_classifier,
            device=self.device
        )
        
        # first, detect open/end events to fix frames to analyze
        
        # skip to specified position
        self.notification_result = self.notification_result.slice(params.start_frame, params.end_frame)
        
        # detect battle open with no players detection
        self.logger.info(f'pre open event process started.')
        pre_open_event = BattleOpenEventCreator(self.frame_rate).create(self.notification_result, None, None, player_detection_enabled=False)
        if pre_open_event is None:
            return None, ErrorCode.BATTLE_OPEN_NOT_FOUND

        # skip to open start positoin 
        self.notification_result = self.notification_result.slice(pre_open_event.start_frame)

        self.logger.info(f'close event process started.')
        processing_time = time.time()
        end_event = BattleEndEventCreator().create(self.notification_result)
        self.logger.info(f'close event process completed. processing time: {time.time() - processing_time}')
        if end_event is None:
            return None, ErrorCode.BATTLE_END_NOT_FOUND
        
        # double check if the end evnt is of the current battle. in the case of invalid match, end event is absense and detect the next battle's end incorrectly
        next_notif_result = self.notification_result.slice(pre_open_event.end_frame + self.frame_rate + 5)
        next_open_event = BattleOpenEventCreator(self.frame_rate).create(next_notif_result, None, None, player_detection_enabled=False)
        if next_open_event is not None and next_open_event.start_frame < end_event.start_frame:
            return None, ErrorCode.BATTLE_END_NOT_FOUND

        # trunc by battle end 
        self.notification_result = self.notification_result.slice(pre_open_event.start_frame, end_event.end_frame)

        # detect basic battle elements frame by frame 
        battle_start_frame = pre_open_event.end_frame
        battle_end_frame = end_event.start_frame
        result_end_frame = battle_end_frame + self.frame_rate * 30 # result view displays at most within 30s after battle end
        
        ikalamp_detector = self._create_ikalamp_process(self.frame_interval, self.preprocess_params.batch_size, battle_start_frame, battle_end_frame)
        ikalamp_detector.start()

        ika_player_detecotr = self._create_ika_player_process(self.frame_interval, self.preprocess_params.batch_size, battle_start_frame, battle_end_frame)
        ika_player_detecotr.start()
        
        indicator_detector = self._create_battle_indicator_process(self.frame_interval, self.preprocess_params.batch_size, battle_start_frame, result_end_frame)
        indicator_detector.start()
            
        ikalamp_detector.join()
        self.ikalamp_result = SharedIkalampDetectionResult.read()

        ika_player_detecotr.join()
        self.ika_player_result = SharedIkaPlayerDetectionResult.read()
        
        indicator_detector.join()
        self.indicator_result = SharedBattleIndicatorDetectionResult.read()
        
        if self.ikalamp_result is None or self.ika_player_result is None or self.indicator_result is None:
            raise InternalError('battle frame analysis failed')
        
        self.logger.info(f'ikalamp process completed. processing time: {self.ikalamp_result.processing_time}')
        self.logger.info(f'ika player process completed. processing time: {self.ika_player_result.processing_time}')
        self.logger.info(f'indicator process completed. processing time: {self.indicator_result.processing_time}')
       
        # remake open event with players detection 
        self.logger.info(f'open event process started.')
        processing_time = time.time()
        open_event = BattleOpenEventCreator(self.frame_rate).create(self.notification_result, self.ikalamp_result, plate_analyzer)
        self.logger.info(f'open event process completed. processing time: {time.time() - processing_time}')
        if open_event is None:
            return None, ErrorCode.BATTLE_OPEN_NOT_FOUND

        self.logger.info(f'result event process started.')
        processing_time = time.time()
        result_event = BattleResultEventCreator(self.preprocess_params.battle_movie_path, open_event, end_event, ocr).create(self.indicator_result)
        self.logger.info(f'result event process completed. processing time: {time.time() - processing_time}')
        if result_event is None:
            return None, ErrorCode.BATTLE_RESULT_NOT_FOUND

        self.logger.info(f'battle info process started.')
        processing_time = time.time()
        battle_info = BattleInfo(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            movie_date=self.preprocess_params.movie_date,
            frame_rate=self.frame_rate,
            open_event=open_event,
            end_event=end_event,
            notify_result=self.notification_result,
            ikalamp_result=self.ikalamp_result,
            ika_player_result=self.ika_player_result,
            indicator_result=self.indicator_result,
            logger=self.logger
        )
        battle_info.build(
            stage_classifier=stage_classifier,
            buki_classifier=buki_classifier,
            weapon_gauge_classifier=weapon_gauge_analyzer,
            ocr=ocr
        )
        self.logger.info(f'battle info process completed. processing time: {time.time() - processing_time}')
        
        first_processing_time = time.time()
        self.logger.info('######## first processing stage started ########')

        self.logger.info(f'special weapon event process started.')
        processing_time = time.time()
        special_weapon_event_creator = SpecialWeaponEventCreator(battle_info, self.model_paths.ikalamp_model_path, self.device, self.preprocess_params.process_id)
        special_weapon_event_creator.create(self.ikalamp_result)
        special_weapon_event_creator.join()
        special_weapon_events = special_weapon_event_creator.events
        self.logger.info(f'special weapon event process completed. processing time: {time.time() - processing_time}')
        if special_weapon_events is None:
            raise InternalError('special weapon event failed')
        
        self.logger.info(f'kill event process started.')
        processing_time = time.time()
        kill_event_creator = KillEventCreator(battle_info, self._create_ocr())
        kill_event_creator.create(self.notification_result, self.ikalamp_result)
        kill_event_creator.join()
        kill_events = kill_event_creator.events
        self.logger.info(f'kill event process completed. processing time: {time.time() - processing_time}')
        if kill_events is None:
            raise InternalError('kill event failed')
        
        self.logger.info(f'death event process started.')
        processing_time = time.time()
        death_event_creator = DeathEventCreator(battle_info, self._create_ocr(), plate_analyzer)
        death_event_creator.create(self.ikalamp_result, self.notification_result)
        death_event_creator.join()
        death_events = death_event_creator.events
        self.logger.info(f'death event process completed. processing time: {time.time() - processing_time}')
        if death_events is None:
            raise InternalError('death event failed')
        
        self.logger.info(f'player number balance event process started.')
        processing_time = time.time()
        player_number_balance_event_creator = PlayerNumberBalanceEventCreator(battle_info)
        player_number_balance_event_creator.create(self.ikalamp_result)
        player_number_balance_event_creator.join()
        player_number_balance_events = player_number_balance_event_creator.events
        self.logger.info(f'player number balance process completed. processing time: {time.time() - processing_time}')
        if player_number_balance_events is None:
            raise InternalError('player number balance event failed')

        self.logger.info(f'player position analysis process started.')
        processing_time = time.time()
        player_position_analyzer = PlayerPositionFrameAnalyzer(self.preprocess_params.battle_movie_path)
        player_position_analyzer.analyze(self.ika_player_result)
        player_position_analyzer.join()
        position_analysis_result = player_position_analyzer.result
        self.logger.info(f'player position process completed. processing time: {time.time() - processing_time}')
        if position_analysis_result is None:
            raise InternalError('player position analysis failed')
        
        self.logger.info(f'indicator analysis process started.')
        processing_time = time.time()
        indicator_analyzer = BattleIndicatorFrameAnalyzer(battle_info, self._create_ocr())
        indicator_analyzer.analyze(self.indicator_result)
        indicator_analyzer.join() 
        indicator_analysis_result = indicator_analyzer.result
        self.logger.info(f'indicator process completed. processing time: {time.time() - processing_time}')
        if indicator_analysis_result is None:
            raise InternalError('indicator analysis failed')
        
        self.logger.info(f'first processing stage ended. processing time: {time.time() - first_processing_time}')
        
        second_processing_time = time.time()
        self.logger.info('######## second processing stage started ########')

        self.logger.info(f'ink tank process started.')
        ink_tank_analyzer = InkTankFrameAnalyzer(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            ink_tank_model_path=self.model_paths.ink_tank_model_path,
            device=self.device
        )
        ink_tank_analyzer.analyze(position_analysis_result)
        
        self.logger.info(f'count down process started.')
        if battle_info.rule == BattleRule.NAWABARI:
            battle_count_event_creator = BattleCountEventCreator(battle_info, ocr, initial_count=0)
            battle_count_event_creator.create(indicator_analysis_result)
        else:
            battle_count_event_creator = BattleCountEventCreator(battle_info, ocr, initial_count=100)
            battle_count_event_creator.create(indicator_analysis_result)
        
        self.logger.info(f'match analysis process started.')
        match_analyzer = MatchFrameAnalyzer(
            battle_movie_path=self.preprocess_params.battle_movie_path,
            match_model_path=self.model_paths.match_model_path,
            device=self.device,
            process_id=self.preprocess_params.process_id,
            ocr=self._create_ocr())
        match_analyzer.analyze(
            notif_result=self.notification_result,
            open_event=open_event,
            result_event=result_event,
            prev_open_event=self.prev_result.battle_info.open_event if self.prev_result else None,
            prev_match=self.prev_result.match_info if self.prev_result else None
        )
        
        ink_tank_analyzer.join()
        ink_tank_result = ink_tank_analyzer.result
        if ink_tank_result is None:
            raise InternalError('ink tank analysis failed')

        battle_count_event_creator.join()
        team_count_events, enemy_count_events = battle_count_event_creator.events
        if team_count_events is None:
            raise InternalError('battle count event failed')
        
        match_analyzer.join()
        match_result = match_analyzer.result
        if match_result is None:
            raise InternalError('match analysis failed')
        
        self.logger.info(f'second processing stage ended. processing time: {time.time() - second_processing_time}')
        
        # complement result counts by count events 
        if result_event.team_count is None and len(team_count_events) > 0:
            result_event.team_count = team_count_events[-1].earned_value
        if result_event.enemy_count is None and len(enemy_count_events) > 0:
            result_event.enemy_count = enemy_count_events[-1].earned_value

        if self.device.startswith('cuda'):
            torch.cuda.empty_cache()

        self.logger.info('analysis completed')
        
        self.prev_result = BattleAnalysisResult(
            version=SPLATOON_VERSION,
            battle_frames=battle_info.battle_end_frame - battle_info.battle_open_frame + 1,
            battle_info=battle_info,
            result_event=result_event,
            kill_events=kill_events,
            death_events=death_events,
            team_count_events=team_count_events,
            enemy_count_events=enemy_count_events,
            player_number_balance_events=player_number_balance_events,
            special_weapon_events=special_weapon_events,
            position_result=position_analysis_result,
            ink_tank_result=ink_tank_result,
            match_info=match_result
        )

        return self.prev_result, None
    
    def _create_ikalamp_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=run_ikalamp_detection,
            args=[
                self.preprocess_params.battle_movie_path,
                self.model_paths.ikalamp_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
    
    def _create_ika_player_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=run_ika_player_detection,
            args=[
                self.preprocess_params.battle_movie_path,
                self.model_paths.ika_player_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
    
    def _create_notification_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=run_notification_detection,
            args=[
                self.preprocess_params.battle_movie_path,
                self.model_paths.notification_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
    
    def _create_battle_indicator_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=run_battle_indicator_detection,
            args=[
                self.preprocess_params.battle_movie_path,
                self.model_paths.battle_indicator_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
    
    def _create_ocr(self) -> SplashFontOCR:
        return SplashFontOCR(
            char_type_model_path=self.model_paths.char_type_model_path,
            hiragana_model_path=self.model_paths.hiragana_model_path,
            katakana_model_path=self.model_paths.katakana_model_path,
            number_model_path=self.model_paths.number_model_path,
            alphabet_model_path=self.model_paths.alphabet_model_path,
            symbol_model_path=self.model_paths.symbol_model_path,
            char_model_path=self.model_paths.char_model_path,
            device=self.device
        )