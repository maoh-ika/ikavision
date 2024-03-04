from dataclasses import dataclass
from enum import Enum
from models.ikalamp import IkalampState
from models.ika_player import IkaPlayer
from prediction.ikalamp_detection_process import IkalampDetectionResult, IkalampDetectionFrame
from events.util import taget_frames_generator, TestResult

class PlayerNumberBalanceState(Enum):
    EVEN = 0
    ADVANTAGE = 1
    DISADVANTAGE = 2

@dataclass
class PlayerNumberBalanceEvent:
    team_number: int
    enemy_number: int
    balance_state: PlayerNumberBalanceState
    start_frame: int
    end_frame: int

class PlayerNumberBalanceMonitor:
    def __init__(self, team_number, enemy_number) -> None:
        self.cur_team_number = team_number
        self.cur_enemy_number = enemy_number
        self.cur_state = self._get_state(team_number, enemy_number)
        self.prev_team_number = team_number
        self.prev_enemy_number = enemy_number
        self.prev_state = self.cur_state

    def _is_balance_changed(self, frame: IkalampDetectionFrame, in_target_frame: bool) -> TestResult:
        if frame.team is None or frame.enemy is None:
            return TestResult.PENDING
        team_number = len(list(filter(lambda l: l.state in [IkalampState.LIVE, IkalampState.SP], frame.team)))
        enemy_number = len(list(filter(lambda l: l.state in [IkalampState.LIVE, IkalampState.SP], frame.enemy)))
        state = self._get_state(team_number, enemy_number)

        if self.cur_state != state or self.cur_team_number != team_number or self.cur_enemy_number != enemy_number:
            self._update(team_number, enemy_number, state)
            return TestResult.NOT_TARGET
        else:
            return TestResult.TARGET
        
    def _update(self, team_number: int, enemy_number: int, state: PlayerNumberBalanceState):
        self.prev_team_number = self.cur_team_number
        self.prev_enemy_number = self.cur_enemy_number
        self.prev_state = self.cur_state
        self.cur_team_number = team_number
        self.cur_enemy_number = enemy_number
        self.cur_state = state
        
    def _get_state(self, team_number: int, enemy_number: int) -> PlayerNumberBalanceState:
        if team_number < enemy_number:
            return PlayerNumberBalanceState.DISADVANTAGE
        elif enemy_number < team_number:
            return PlayerNumberBalanceState.ADVANTAGE
        else:
            return PlayerNumberBalanceState.EVEN

class PlayerNumberBalanceEventCreator:
    def __init__(self, team: list[IkaPlayer], enemy: list[IkaPlayer]) -> None:
        super().__init__(name='PlayerNumberBalanceEventCreator')
        self.team = team
        self.enemy = enemy
        self.ikalamp_result: IkalampDetectionResult = None
        self.events: list[PlayerNumberBalanceEvent] = None

    def create(self, ikalamp_result: IkalampDetectionResult) -> list[PlayerNumberBalanceEvent]:
        events = []
        lamp_frames = ikalamp_result.get_sliced_frames()
        max_team_number, max_enemy_number = self._get_team_member_count(ikalamp_result)
        state_monitor = PlayerNumberBalanceMonitor(team_number=max_team_number, enemy_number=max_enemy_number)
        generator = taget_frames_generator(lamp_frames, state_monitor._is_balance_changed, exit_test_frame_count=1)
        for state_frames, _, _ in generator:
            event = PlayerNumberBalanceEvent(
                team_number=state_monitor.prev_team_number,
                enemy_number=state_monitor.prev_enemy_number,
                balance_state=state_monitor.prev_state,
                start_frame=state_frames[0].frame,
                end_frame=state_frames[-1].frame
            )
            events.append(event)

        return events

    def _get_team_member_count(self, ikalamp_result: IkalampDetectionResult) -> int:
        team_number = len(self.team)
        enemy_number = len(self.enemy)
        lamp_frames = ikalamp_result.get_sliced_frames()
        if team_number == 0:
            for frame in lamp_frames:
                if frame.team is not None:
                    team_number = len(frame.team)
        if enemy_number == 0:
            for frame in lamp_frames:
                if frame.enemy is not None:
                    enemy_number = len(frame.enemy)

        return team_number, enemy_number