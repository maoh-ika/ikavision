from multiprocessing import Value
from enum import Enum
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from prediction.ikalamp_detection_process import IkalampDetectionFrame
from prediction.ika_player_detection_process import IkaPlayerDetectionFrame 
from prediction.notification_detection_process import NotificationDetectionFrame
from prediction.battle_indicator_detection_process import BattleIndicatorDetectionFrame
from prediction.plate_frame_analyzer import PlateAnalysisFrame
from prediction.ink_tank_frame_analyzer import InkTankAnalysisFrame
from models.ika_player import IkaPlayer, IkaPlayerPosition
from models.battle import BattleSide
from models.battle_info import BattleInfo
from models.notification import NotificationType
from models.ikalamp import Ikalamp, IkalampTimer
from models.buki import Buki
from events.death_event import DeathEvent
from events.kill_event import KillEvent
from events.battle_countdown_event import BattleCountEvent
from events.special_weapon_event import SpecialWeaponEvent, SpecialWeaponEventType
from events.battle_result_event import BattleResultEvent
from battle_analyzer import BattleAnalysisResult

class PlayerState(Enum):
    STOP = 0
    PLAY = 1

class Player:

    def __init__(self,
        ikalamp_model_path: str,
        ika_model_path: str,
        notification_model_path: str,
        plate_model_path: str
    ) -> None:
        self.ikalamp_model = YOLO(ikalamp_model_path)
        self.ika_model = YOLO(ika_model_path)
        self.notification_model = YOLO(notification_model_path)
        self.plate_model = YOLO(plate_model_path)
        self.state = PlayerState.STOP

    def play(self, result: BattleAnalysisResult):
        
        cap = cv2.VideoCapture(result.battle_info.battle_movie_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_number = result.battle_info.battle_open_frame
        self.state = PlayerState.PLAY
        showBuki = True

        position_dict = { frame.frame: frame for frame in result.position_result.frames }
        ink_dict = { frame.frame: frame for frame in result.ink_tank_result.frames }

        buki_images = self.load_buki_images(result.battle_info)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        shutdown = False
        while not shutdown:
            while self.state == PlayerState.PLAY:
                ret, img = cap.read()
                if not ret:
                    break
                
                lamp = result.battle_info.ikalamp.get_frame(frame_number)
                if lamp and lamp.team:
                    lamp_annotator = Annotator(img, line_width=1, example=str(self.ikalamp_model.model.names))
                    self.draw_ikalamps(lamp, lamp_annotator)
                    player_name_annotator = Annotator(img, line_width=1, font_size=12, example='あ')
                    self.draw_player_names(result.battle_info.team_players, result.battle_info.enemy_players, lamp, result.battle_info, 2, player_name_annotator)
                    img = np.array(player_name_annotator.im)
                    self.draw_kill_death_count(img, frame_number, lamp, result.death_events, result.kill_events, 30)
                    self.draw_sp_count(img, frame_number, lamp, result.special_weapon_events)
                
                if showBuki and lamp and lamp.team:
                    self.draw_buki(img, lamp.team, result.battle_info.team_bukis, buki_images, 50)
                    self.draw_buki(img, lamp.enemy, result.battle_info.enemy_bukis, buki_images, 50)
                
                position = result.battle_info.ika_player.get_frame(frame_number)
                if position:
                    main_player_position = position_dict[frame_number].main_player_position if frame_number in position_dict else None
                    ika_annotator = Annotator(img, line_width=1, example=str(self.ika_model.model.names))
                    self.draw_positions(img, position, main_player_position, ika_annotator)
                
                notification = result.battle_info.notification.get_frame(frame_number)
                if notification:
                    notification_annotator = Annotator(img, line_width=1, example=str(self.notification_model.model.names))
                    self.draw_notifications(notification, notification_annotator)
                    kill_annotator = Annotator(img, line_width=1, font_size=12, example='あ')
                    self.draw_kill_death_events(notification, result.kill_events, result.death_events, result.battle_info, kill_annotator)
                    img = np.array(kill_annotator.im)

                indicator = result.battle_info.indicator.get_frame(frame_number)
                if indicator and lamp and lamp.timer:
                    self.draw_count(img, indicator, result.team_count_events, result.enemy_count_events, lamp.timer)

                if result.result_event.start_frame <= frame_number and frame_number <= result.result_event.end_frame:
                    self.draw_result(img, result.result_event)
                
#                if frame_number in plate_result.frames:
#                    plate_annotator = Annotator(img, line_width=1, font_size=12, example='あ')
#                    plate = plate_result.frames[frame_number]
#                    self.draw_plate(plate, plate_annotator)
#                    img = np.array(plate_annotator.im)

                if frame_number in ink_dict:
                    self.draw_ink_tank(img, ink_dict[frame_number])

                #map_frame =  map_segment_result.get_frame(frame_number)                
                self.draw_debug_info(img, frame_number, total_frames, result.battle_info, '')

                cv2.imshow("test", img)
                key = cv2.waitKey(33)
                if key == ord(','):
                    frame_number -= 10
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                elif key == ord('.'):
                    frame_number += 10
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                elif key == ord(' '):
                    self.state = PlayerState.STOP
                elif key == ord('b'):
                    showBuki = not showBuki

                frame_number += 1
                end_frame = result.result_event.end_frame if result.result_event else result.battle_info.battle_end_frame
                if frame_number >= end_frame:
                    self.state = PlayerState.STOP
            
            key = cv2.waitKey(33)
            if key == ord(','):
                frame_number -= 10
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            elif key == ord('.'):
                frame_number += 10
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            elif key == ord(' '):
                self.state = PlayerState.PLAY
            elif key == ord('b'):
                showBuki = not showBuki
            elif key == 27:
                shutdown = True

        cap.release() 
        cv2.destroyAllWindows()
        print('Display main ended')

    def draw_ikalamps(self, ikalamps: IkalampDetectionFrame, annotator: Annotator):
        for lamp in ikalamps.team:
            self.draw_bbox(lamp.xyxy, lamp.state.name, lamp.state.value, lamp.conf, annotator)
        for lamp in ikalamps.enemy:
            self.draw_bbox(lamp.xyxy, lamp.state.name, lamp.state.value, lamp.conf, annotator)
        self.draw_bbox(ikalamps.timer.xyxy, ikalamps.timer.state.name, ikalamps.timer.state.value, ikalamps.timer.conf, annotator)
    
    def draw_positions(self, img, position: IkaPlayerDetectionFrame, main_player_position: IkaPlayerPosition, annotator: Annotator):
        for pos in position.positions:
            self.draw_bbox(pos.xyxy, f'{pos.form.name}_{pos.track_id}', pos.form.value, pos.conf, annotator)
        for name in position.names:
            self.draw_bbox(name.xyxy, 'name', name.cls, name.conf, annotator)
        if main_player_position:
            xyxy = main_player_position.xyxy
            cv2.rectangle(img, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0,255,255), 3)
    
    def draw_notifications(self,
        notification: NotificationDetectionFrame, annotator: Annotator):
        for notif in notification.notifications:
            self.draw_bbox(notif.xyxy, notif.type.name, notif.type.value, notif.conf, annotator)

    def draw_kill_death_events(self,
        notification: NotificationDetectionFrame,
        kill_events: list[KillEvent],
        death_events: list[DeathEvent],
        battle_info: BattleInfo,
        annotator):
        for notif in notification.notifications:
            if notif.type == NotificationType.NOTIFICATION_KILL:
                evts = list(filter(lambda e: e.start_frame <= notification.frame and notification.frame <= e.end_frame, kill_events))
                if len(evts) > 0:
                    name = evts[0].death_player.name if evts[0].death_player else 'UNKNOWN'
                    annotator.text((notif.xyxy[0], notif.xyxy[1] - 40), f'KILL: {name}', (255,0,0))
            elif notif.type == NotificationType.NOTIFICATION_DEATH_REASON:
                def _is_main_player(evt: DeathEvent):
                    if battle_info.main_player is None:
                        return False
                    in_range = evt.start_frame <= notification.frame and notification.frame <= evt.end_frame
                    has_main = battle_info.main_player is not None and evt.death_player is not None
                    main_ord = battle_info.main_player.lamp_ord == evt.death_player.lamp_ord
                    team_side = evt.death_player.side == BattleSide.TEAM
                    return in_range and has_main and main_ord and team_side

                evts = list(filter(lambda e:  _is_main_player(e), death_events))
                if len(evts) > 0:
                    name = evts[0].kill_player.name if evts[0].kill_player else 'UNKNOWN'
                    reason = evts[0].death_reason
                    annotator.text((notif.xyxy[2], notif.xyxy[3] - 20), f'REASON: {reason}', (255,0,0))
                    annotator.text((notif.xyxy[2], notif.xyxy[3] - 40), f'KILLER: {name}', (255,0,0))

    def draw_plate(self, plate: PlateAnalysisFrame, annotator: Annotator):
        for plt  in plate.plates:
            if plt.player_id:
                for c in plt.player_id.value:
                    annotator.rectangle(c.xyxy, outline=(255,0,0,100), width=2)
                self.draw_bbox(plt.player_id.xyxy, f'player_id_{plt.player_id.text}', 0, plt.player_id.conf, annotator)
            if plt.player_name:
                for c in plt.player_name.value:
                    annotator.rectangle(c.xyxy, outline=(0,255,0,100), width=2)
                self.draw_bbox(plt.player_name.xyxy, f'player_name_{plt.player_name.text}', 1, plt.player_name.conf, annotator)
            if plt.nickname:
                for c in plt.nickname.value:
                    annotator.rectangle(c.xyxy, outline=(0,0,255,100), width=2)
                self.draw_bbox(plt.nickname.xyxy, f'nickname_{plt.nickname.text}', 2, plt.nickname.conf, annotator)
            for badge in plt.badges:
                self.draw_bbox(badge.xyxy, 'badge', 3, badge.conf, annotator)

    def draw_player_names(self, team: list[IkaPlayer], enemy: list[IkaPlayer], lamp: IkalampDetectionFrame, battle_info: BattleInfo, offset_y, annotator):
        for l in lamp.team:
            if l.ord < len(team):
                txt_color = (0, 0, 255) if battle_info.main_player and l.ord == battle_info.main_player.lamp_ord else (255, 255, 255)
                annotator.text((l.xyxy[0], l.xyxy[3] + offset_y), team[l.ord].name, txt_color=txt_color)
        for l in lamp.enemy:
            if l.ord < len(enemy):
                annotator.text((l.xyxy[0], l.xyxy[3] + offset_y), enemy[l.ord].name)

    def draw_ink_tank(self, img, ink_tank: InkTankAnalysisFrame):
        if ink_tank.main_player_ink:
            if ink_tank.main_player_ink.consumed:
                img[ink_tank.main_player_ink.consumed.mask[:, 1], ink_tank.main_player_ink.consumed.mask[:, 0]] = (255,0,255)
            if ink_tank.main_player_ink.remaining:
                img[ink_tank.main_player_ink.remaining.mask[:, 1], ink_tank.main_player_ink.remaining.mask[:, 0]] = (0,0,255)
    
    def draw_kill_death_count(self, img, frame: int, lamp: IkalampDetectionFrame, death_events: list[DeathEvent], kill_events: list[KillEvent], offset_y):
        for l in lamp.team:
            kill_count = len(list(filter(lambda e: e.start_frame <= frame and e.kill_player.side == BattleSide.TEAM and e.kill_player.lamp_ord == l.ord, kill_events)))
            death_count = len(list(filter(lambda e: e.start_frame <= frame and e.death_player.side == BattleSide.TEAM and e.death_player.lamp_ord == l.ord, death_events)))
            self.draw_text(img, str(kill_count), (l.xyxy[0], l.xyxy[3] + offset_y), 1, (0,0,255))
            self.draw_text(img, str(death_count), (l.xyxy[0]+20, l.xyxy[3] + offset_y), 1, (255,0,0))
        for l in lamp.enemy:
            death_count = len(list(filter(lambda e: e.start_frame <= frame and e.death_player.side == BattleSide.ENEMY and e.death_player.lamp_ord == l.ord, death_events)))
            self.draw_text(img, str(death_count), (l.xyxy[0], l.xyxy[3] + offset_y), 1, (255,0,0))
    
    def draw_sp_count(self, img, frame: int, lamp: IkalampDetectionFrame, sp_events: list[DeathEvent]):
        for l in lamp.team:
            events = list(filter(lambda e: e.start_frame <= frame and e.player.side == BattleSide.TEAM and e.player.lamp_ord == l.ord, sp_events))
            charge = len(list(filter(lambda e: e.type == SpecialWeaponEventType.FULLY_CHARGED and e.start_frame <= frame, events)))
            trigger = len(list(filter(lambda e: e.type == SpecialWeaponEventType.TRIGGERED and e.start_frame <= frame, events)))
            spoil = len(list(filter(lambda e: e.type == SpecialWeaponEventType.SPOILED and e.start_frame <= frame, events)))
            self.draw_text(img, str(charge), (l.xyxy[0], l.xyxy[1] + 10), 1, (255,0,0))
            self.draw_text(img, str(trigger), (l.xyxy[0] + 15, l.xyxy[1] + 10), 1, (0,255,0))
            self.draw_text(img, str(spoil), (l.xyxy[0] + 30, l.xyxy[1] + 10), 1, (0,0,255))
        for l in lamp.enemy:
            events = list(filter(lambda e: e.start_frame <= frame and e.player.side == BattleSide.ENEMY and e.player.lamp_ord == l.ord, sp_events))
            charge = len(list(filter(lambda e: e.type == SpecialWeaponEventType.FULLY_CHARGED and e.start_frame <= frame, events)))
            trigger = len(list(filter(lambda e: e.type == SpecialWeaponEventType.TRIGGERED and e.start_frame <= frame, events)))
            spoil = len(list(filter(lambda e: e.type == SpecialWeaponEventType.SPOILED and e.start_frame <= frame, events)))
            self.draw_text(img, str(charge), (l.xyxy[0], l.xyxy[1] + 10), 1, (255,0,0))
            self.draw_text(img, str(trigger), (l.xyxy[0] + 16, l.xyxy[1] + 10), 1, (0,255,0))
            self.draw_text(img, str(spoil), (l.xyxy[0] + 31, l.xyxy[1] + 10), 1, (0,0,255))

    def draw_buki(self, img, team_lamps: list[Ikalamp], team_bukis: list[Buki], buki_images: dict, offset_y: int):
        for lamp in team_lamps:
            buki = team_bukis[lamp.ord]
            main_img = buki_images[buki.main_weapon.name]
            sub_img = buki_images[buki.sub_weapon.name]
            sp_img = buki_images[buki.sp_weapon.name]
            x = lamp.xyxy[0]
            y = lamp.xyxy[3] + offset_y
            img[y:y+main_img.shape[0],x:x+main_img.shape[1]] = main_img
            x = lamp.xyxy[0]
            y = y + main_img.shape[0]
            img[y:y+sub_img.shape[0],x:x+sub_img.shape[1]] = sub_img
            x = x + sub_img.shape[1]
            img[y:y+sp_img.shape[0],x:x+sp_img.shape[1]] = sp_img

    def draw_count(self, img, frame: BattleIndicatorDetectionFrame, team_counts: list[BattleCountEvent], enemy_counts: list[BattleCountEvent], timer: IkalampTimer):
        if frame.indicator is None:
            return
        counts = list(filter(lambda evt: evt.start_frame <= frame.frame and frame.frame <= evt.end_frame, team_counts))
        if len(counts) > 0 and len(frame.indicator.counts) > 0:
            x = timer.xyxy[0] - 10
            y = timer.xyxy[3] + 5
            self.draw_text(img, str(counts[0].count), (x, y), 1, (255,0,0))
        counts = list(filter(lambda evt: evt.start_frame <= frame.frame and frame.frame <= evt.end_frame, enemy_counts))
        if len(counts) > 0 and len(frame.indicator.counts) > 1:
            x = timer.xyxy[2] - 40
            y = timer.xyxy[3] + 5
            self.draw_text(img, str(counts[0].count), (x, y), 1, (0,0,255))
    
    def draw_result(self, img, result_event: BattleResultEvent):
        text = f'{result_event.win_lose.name} {result_event.team_count} / {result_event.enemy_count}'
        self.draw_text(img, text, (100, 100), 1, (255,0,0))

    def draw_debug_info(self, img, frame_number, total_frames, battle_info: BattleInfo, segment_id: str):
        frame_pos = f'{frame_number}/{total_frames}'
        self.draw_text(img, frame_pos, (10, 30), 1, color=(0,0,255))
        self.draw_text(img, battle_info.stage.name, (10, 60), 1, color=(0,0,255))
        self.draw_text(img, battle_info.rule.name, (10, 90), 1, color=(0,0,255))
        team_color = battle_info.team_color.color if battle_info.team_color else (128, 128, 128)
        cv2.rectangle(img, (10, 120), (50, 160), team_color, -1)
        enemy_color = battle_info.enemy_color.color if battle_info.enemy_color else (128, 128, 128)
        cv2.rectangle(img, (60, 120), (100, 160), enemy_color, -1)

    def draw_bbox(self, xyxy, label, cls, conf, annotator):
        label =  f'{label} {conf:.2f}'
        annotator.box_label(xyxy, label, color=colors(cls, True))

    def draw_text(self, img, text, pos, size, color=(0,0,0)):
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, size, color, 2)

    def load_buki_images(self, battle_info: BattleInfo) -> dict:
        main_img_dir = './battle_analyzer/images/mainWeapons/'
        sub_img_dir = './battle_analyzer/images/subWeapons/'
        sp_img_dir = './battle_analyzer/images/spWeapons/'
        main_size = (48, 48)
        wp_size = (24, 24)
        buki_images = {}

        def _load(wp: Enum, img_dir: str, size: tuple):
            path = f'{img_dir}{Buki.get_buki_id(wp)}.png'
            img = cv2.imread(path)
            return cv2.resize(img, size, interpolation=cv2.INTER_AREA)

        for buki in battle_info.team_bukis:
            buki_images[buki.main_weapon.name] = _load(buki.main_weapon, main_img_dir, main_size)
            buki_images[buki.sub_weapon.name] = _load(buki.sub_weapon, sub_img_dir, wp_size)
            buki_images[buki.sp_weapon.name] = _load(buki.sp_weapon, sp_img_dir, wp_size)
        for buki in battle_info.enemy_bukis:
            buki_images[buki.main_weapon.name] = _load(buki.main_weapon, main_img_dir, main_size)
            buki_images[buki.sub_weapon.name] = _load(buki.sub_weapon, sub_img_dir, wp_size)
            buki_images[buki.sp_weapon.name] = _load(buki.sp_weapon, sp_img_dir, wp_size)

        return buki_images