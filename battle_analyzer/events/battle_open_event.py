from dataclasses import dataclass
from models.battle import BattleRule, BattleSide, BattleStage
from models.ika_player import IkaPlayer
from models.ikalamp import IkalampState
from models.text import likely_text
from models.notification import NotificationType, Notification
from prediction.frame import Frame
from prediction.notification_detection_process import NotificationDetectionFrame, NotificationDetectionResult
from prediction.ikalamp_detection_process import IkalampDetectionFrame, IkalampDetectionResult
from prediction.plate_frame_analyzer import PlateFrameAnalyzer
from events.util import taget_frames_generator, TestResult
from utils import likely_value

@dataclass
class BattleOpenEvent:
    team: list[IkaPlayer]
    enemy: list[IkaPlayer]
    rule: BattleRule
    start_frame: int
    end_frame: int

class BattleOpenEventCreator:
    def __init__(self, frame_rate: int) -> None:
        self.frame_rate = frame_rate

    def create(self,
        notif_result: NotificationDetectionResult,
        ikalamp_result: IkalampDetectionResult,
        plate_analyzer: PlateFrameAnalyzer,
        player_detection_enabled: bool=True) -> BattleOpenEvent:
        notif_frames = notif_result.get_sliced_frames()
        generator = taget_frames_generator(notif_frames, self._is_opening_frame, exit_test_frame_count=30)
        for open_frames, _, end_idx in generator:
            if len(open_frames) == 0:
                continue
            
            start_frame = open_frames[0].frame
            end_frame = open_frames[-1].frame
            
            rule = self._find_rule(open_frames)
            if rule is None:
                continue
            
            if not player_detection_enabled:
                return BattleOpenEvent(
                    team=[],
                    enemy=[],
                    rule=rule,
                    start_frame=start_frame,
                    end_frame=end_frame
                )

            team_member_count, enemy_member_count = self._count_players(ikalamp_result.slice(end_frame, end_frame + self.frame_rate * 60))
            if team_member_count is None or enemy_member_count is None:
                continue
        
            team, enemy = self._find_players(open_frames, plate_analyzer, team_member_count, enemy_member_count)
            if team is None or enemy is None:
                continue

            return BattleOpenEvent(
                team=team,
                enemy=enemy,
                rule=rule,
                start_frame=start_frame,
                end_frame=end_frame
            )
        
        return None
    
    def _is_opening_frame(self, frame: NotificationDetectionFrame, in_target_frame: bool) -> TestResult:
        is_target = self._find_rule_notification(frame) and len(self._find_plate_notifications(frame)) >= 2
        return TestResult.TARGET if is_target else TestResult.NOT_TARGET
    
    def _count_players(self, ikalamp_result: IkalampDetectionResult) -> (int, int):
        def _to_team_value(frame: IkalampDetectionFrame) -> int:
           if frame.team is None:
               return None
           return len(list(filter(lambda i: i.state != IkalampState.DROP , frame.team)))
        def _to_enemy_value(frame: IkalampDetectionFrame) -> int:
           if frame.enemy is None:
               return None
           return len(list(filter(lambda i: i.state != IkalampState.DROP , frame.enemy)))

        frames = ikalamp_result.get_sliced_frames()
        team_count = likely_value(frames, _to_team_value)
        enemy_count = likely_value(frames, _to_enemy_value)

        return team_count, enemy_count
    
    def _find_rule(self, frames: list[NotificationDetectionFrame]) -> BattleStage:
        def _to_rule(frame: NotificationDetectionFrame) -> BattleStage:
            rule_notif = self._find_rule_notification(frame)
            return self._to_battle_rule(rule_notif) if rule_notif else None
        
        return likely_value(frames, _to_rule)

    def _find_players(self,
        opening_frames: [NotificationDetectionFrame],
        plate_analyzer: PlateFrameAnalyzer,
        team_member_count: int,
        enemy_number_count: int
    ) -> (list[IkaPlayer], list[IkaPlayer]):
        # find most precisely detected opening frame
        likely_plate_count = team_member_count + enemy_number_count
        precise_frames = []
        for frame in opening_frames:
            plate_notifs = self._find_plate_notifications(frame)
            plate_count = len(plate_notifs)
            if likely_plate_count == plate_count:
                precise_frames.append(frame)

        if len(precise_frames) == 0:
            return None, None
        
        # opening frames should include stage notification
        rule_notif = self._find_rule_notification(precise_frames[0])
        if rule_notif is None:
            return None, None

        # detect players from plates in opening frames 
        team_candidates = []
        enemy_candidates = []
        for frame in precise_frames:
           team, enemy = self._analyze_players(frame, likely_plate_count, rule_notif, plate_analyzer)
           if team is None or enemy is None or len(team) != team_member_count or len(enemy) != enemy_number_count:
               continue
           team_candidates.append(team)
           enemy_candidates.append(enemy)

        if len(team_candidates) == 0 or len(enemy_candidates) == 0:
            return None, None

        # fix each player by comparing attributes between frames
        fixed_team = []
        for ord in range(len(team_candidates[0])):
            player_candidates = list(map(lambda team: team[ord], team_candidates))
            fixed_team.append(self._fix_player(player_candidates))
        
        fixed_enemy = []
        for ord in range(len(enemy_candidates[0])):
            player_candidates = list(map(lambda team: team[ord], enemy_candidates))
            fixed_enemy.append(self._fix_player(player_candidates))

        return fixed_team, fixed_enemy        

    def _analyze_players(self,
        frame: Frame,
        player_count: int,
        rule_notif: Notification,
        plate_analyzer: PlateFrameAnalyzer) -> (list[IkaPlayer], list[IkaPlayer]):
        result = plate_analyzer.analyze([frame])
        if len(result.frames[0].plates) != player_count:
            return None, None

        team_plates = []
        enemy_plates = []        
        center_x = (rule_notif.xyxy[2] + rule_notif.xyxy[0]) / 2
        for plate in result.frames[0].plates:
            if plate.xyxy[0] < center_x:
                team_plates.append(plate)
            elif center_x < plate.xyxy[0]:
                enemy_plates.append(plate)

        if len(team_plates) + len(enemy_plates) != player_count:
            return None, None

        team_players = []
        for idx, plate in enumerate(sorted(team_plates, key=lambda p: p.xyxy[1])):
            player = IkaPlayer(
                id=plate.player_id.text if plate.player_id else '',
                name=plate.player_name.text if plate.player_name else '',
                nickname=plate.nickname.text if plate.nickname else '',
                side=BattleSide.TEAM,
                lamp_ord=idx
            )
            team_players.append(player)
        
        enemy_players = []
        for idx, plate in enumerate(sorted(enemy_plates, key=lambda p: p.xyxy[1])):
            player = IkaPlayer(
                id=plate.player_id.text if plate.player_id else '',
                name=plate.player_name.text if plate.player_name else '',
                nickname=plate.nickname.text if plate.nickname else '',
                side=BattleSide.ENEMY,
                lamp_ord=idx
            )
            enemy_players.append(player)

        return team_players, enemy_players

    def _find_rule_notification(self, frame: NotificationDetectionFrame) -> Notification:
        for notif in frame.notifications:
            if notif.type in [
                NotificationType.NOTIFICATION_RULE_NAWABARI,
                NotificationType.NOTIFICATION_RULE_HOKO,
                NotificationType.NOTIFICATION_RULE_YAGURA,
                NotificationType.NOTIFICATION_RULE_ASARI,
                NotificationType.NOTIFICATION_RULE_AREA
            ]:
                return notif
        return None
    
    def _find_plate_notifications(self, frame: NotificationDetectionFrame) -> list[Notification]:
        return list(filter(lambda n: n.type == NotificationType.NOTIFICATION_PLAYER_PLATE, frame.notifications))
    
    def _fix_player(self, candidates: list[IkaPlayer]) -> IkaPlayer:
        player_names = []
        player_ids = []
        nicknames = []
        for ika in candidates:
            if ika.name != '':
                player_names.append(ika.name)
            if ika.id != '':
                player_ids.append(ika.id)
            if ika.nickname != '':
                nicknames.append(ika.nickname)
        
        return IkaPlayer(
            id=likely_text(player_ids),
            name=likely_text(player_names),
            nickname=likely_text(nicknames),
            side=candidates[0].side,
            lamp_ord=candidates[0].lamp_ord
        )
    
    def _to_battle_rule(self, rule_notif: Notification) -> BattleSide:
        if rule_notif.type == NotificationType.NOTIFICATION_RULE_NAWABARI:
            return BattleRule.NAWABARI
        elif rule_notif.type == NotificationType.NOTIFICATION_RULE_HOKO:
            return BattleRule.HOKO
        elif rule_notif.type == NotificationType.NOTIFICATION_RULE_YAGURA:
            return BattleRule.YAGURA
        elif rule_notif.type == NotificationType.NOTIFICATION_RULE_ASARI:
            return BattleRule.ASARI
        elif rule_notif.type == NotificationType.NOTIFICATION_RULE_AREA:
            return BattleRule.AREA
        else:
            return BattleRule.UNKNOWN
        