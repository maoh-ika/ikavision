from dataclasses import dataclass
from enum import Enum
from threading import Thread
from multiprocessing import Value
from models.ika_player import IkaPlayer
from models.battle import BattleSide
from models.battle_info import BattleInfo
from models.ikalamp import IkalampState
from prediction.ikalamp_detection_process import IkalampDetectionResult, IkalampDetectionFrame, run_ikalamp_detection
from events.util import taget_frames_generator, find_target_frames, TestResult
from error import InternalError

class SpecialWeaponEventType(Enum):
    FULLY_CHARGED = 0
    TRIGGERED = 1
    SPOILED = 2

@dataclass
class SpecialWeaponEvent:
    type: SpecialWeaponEventType
    player: IkaPlayer
    start_frame: int
    end_frame: int

class SpecialWeaponEventCreator(Thread):
    def __init__(self, battle_info: BattleInfo, ikalamp_model_path: str, device: str, process_id: int) -> None:
        super().__init__(name='SpecialWeaponEventCreator')
        self.battle_info = battle_info
        self.ikalamp_model_path = ikalamp_model_path
        self.device = device
        self.process_id = process_id
        self.ikalamp_result: IkalampDetectionResult = None
        self.events: list[SpecialWeaponEvent] = None
        self.sp_frames_thresh = 2
    
    def create(self, ikalamp_result: IkalampDetectionResult) -> list[SpecialWeaponEvent]:
        self.ikalamp_result = ikalamp_result
        self.start()

    def run(self):
        if self.ikalamp_result is None:
            raise InternalError('run must be called via create')
        events = []
        ikalamp_frames = self.ikalamp_result.slice(self.ikalamp_result.start_frame, self.battle_info.end_event.start_frame).get_sliced_frames()
        players = self.battle_info.team_players + self.battle_info.enemy_players
        for player in players:
            generator = taget_frames_generator(ikalamp_frames, self._make_test_func(player.side, player.lamp_ord), exit_test_frame_count=5)
            for sp_frames, _, end_idx in generator:
                if len(sp_frames) == 0:
                    continue
                if len(sp_frames) < self.sp_frames_thresh: # at least two consecutive frames
                    # inspect frames that skipped analysis
                    if (
                        not self._is_sp_period(sp_frames[0].frame - self.sp_frames_thresh + 1, sp_frames[0].frame - 1, player.side, player.lamp_ord) and
                        not self._is_sp_period(sp_frames[-1].frame + 1, sp_frames[-1].frame + self.sp_frames_thresh - 1, player.side, player.lamp_ord)
                        ):
                        continue
                event = self._make_fully_charted(player, sp_frames[0])
                events.append(event)
                event = self._make_triggered_or_spoiled(player, sp_frames[-1], end_idx, ikalamp_frames)
                if event is not None:
                    events.append(event)

        self.events = events
    
    def _is_sp_frame(self, frame: IkalampDetectionFrame, in_target_frame: bool, side: BattleSide, ord: int) -> TestResult:
        if frame.team is None or frame.enemy is None:
            return TestResult.PENDING
        if side == BattleSide.TEAM:
            return TestResult.TARGET if frame.team[ord].state == IkalampState.SP else TestResult.NOT_TARGET
        else:
            return TestResult.TARGET if frame.enemy[ord].state == IkalampState.SP else TestResult.NOT_TARGET
        
    def _make_test_func(self, side: BattleSide, ord: int):
        return lambda frame, in_target_frame: self._is_sp_frame(frame, in_target_frame, side, ord)
    
    def _make_fully_charted(self, player: IkaPlayer, sp_start_frame: IkalampDetectionFrame) -> SpecialWeaponEvent:
        return SpecialWeaponEvent(
            type=SpecialWeaponEventType.FULLY_CHARGED,
            player=player,
            start_frame=sp_start_frame.frame,
            end_frame=sp_start_frame.frame
        )
    
    def _make_triggered_or_spoiled(self,
        player: IkaPlayer,
        sp_end_frame: IkalampDetectionFrame,
        sp_end_index: int,
        frames: list[IkalampDetectionFrame]
    ) -> SpecialWeaponEvent:
        next_frame_idx = sp_end_index + 1
        if len(frames) <= next_frame_idx:
            return None # battle is over

        evt_type = None
        evt_frame = sp_end_frame.frame
        for lamp_frame in frames[next_frame_idx:]:
            if player.side == BattleSide.TEAM and lamp_frame.team is not None:
                if lamp_frame.team[player.lamp_ord].state == IkalampState.LIVE:
                    evt_type = SpecialWeaponEventType.TRIGGERED
                else:
                    evt_type = SpecialWeaponEventType.SPOILED
                break
            elif player.side == BattleSide.ENEMY and lamp_frame.enemy is not None:
                if lamp_frame.enemy[player.lamp_ord].state == IkalampState.LIVE:
                    evt_type = SpecialWeaponEventType.TRIGGERED
                else:
                    evt_type = SpecialWeaponEventType.SPOILED
                break
            evt_frame = lamp_frame.frame
        if evt_type is None:
            return None
        
        return SpecialWeaponEvent(
            type=evt_type,
            player=player,
            start_frame=evt_frame,
            end_frame=evt_frame
        )

    def _is_sp_period(self, start_frame: int, end_frame: int, side: BattleSide, ord: int) -> bool:
        result = run_ikalamp_detection(
            battle_movie_path=self.battle_info.battle_movie_path,
            ikalamp_model_path=self.ikalamp_model_path,
            frame_interval=1,
            device=self.device,
            process_id=self.process_id,
            batch_size=end_frame - start_frame + 1,
            start_frame=start_frame,
            end_frame=end_frame,
            write_shared_memory=False
        )
        if result is None:
            return False
        
        start_idx, end_idx = find_target_frames(result.frames, self._make_test_func(side, ord), exit_test_frame_count=1)
        if start_idx is None or end_idx is None:
            return False
        return (end_idx - start_idx) == (end_frame - start_frame)
