from dataclasses import dataclass
import numpy as np
import Levenshtein
import cv2
from models.text import to_str, likely_text
from prediction.ika_player_detection_process import IkaPlayerDetectionFrame
from prediction.splash_font_ocr import SplashFontOCR
from utils import class_to_dict, hstack, MovieReader
from models.ink_color import InkColor
from models.ika_player import IkaPlayer
from models.battle import BattleSide
from models.detected_item import TrackableItem

@dataclass
class PlayerNameItem:
    player: IkaPlayer
    start_frame: int
    end_frame: int
    track_id: int
    
    @classmethod
    def from_json(cls, j):
        return cls(
            player=IkaPlayer.from_json(j['player']),
            start_frame=j['start_frame'],
            end_frame=j['end_frame'],
            track_id=j['track_id'],
        )

@dataclass
class PlayerNameAnalysisFrame:
    frame: int
    players: list[PlayerNameItem]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            frame=j['frame'],
            players=[PlayerNameItem.from_json(t) for t in j['players']]
        )
    
@dataclass
class PlayerNameAnalysisResult:
    frames: list[PlayerNameAnalysisFrame]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            frames=[PlayerNameAnalysisFrame.from_json(t) for t in j['frames']]
        )
    
    def to_dict(self):
        return class_to_dict(self)

class PlayerNameFrameAnalyzer:
    def __init__(self,
            battle_movie_path: str,
            team_players: list[IkaPlayer],
            enemy_players: list[IkaPlayer],
            team_color: InkColor,
            enemy_color: InkColor,
            ocr: SplashFontOCR
        ) -> None:
        self.team_players = team_players
        self.enemy_players = enemy_players
        self.team_color = team_color
        self.enemy_color = enemy_color
        self.ocr = ocr
        self.reader = MovieReader(battle_movie_path)

    def analyze(self, frames: [IkaPlayerDetectionFrame]) -> PlayerNameAnalysisResult:
        name_frames = {}
        tracking_names = {}
        for frame in frames:
            for name in frame.names:
                if name.track_id is None:
                    continue
                if name.track_id in tracking_names:
                    # coutinue to track
                    tracking_names[name.track_id].append((name, frame.frame))
                else:
                    # found new tracking item
                    tracking_names[name.track_id] = [(name, frame.frame)]

        for name_items in tracking_names.values():
            if len(name_items) == 0:
                continue
            name_frame = self._make_name_item(name_items)
            if name_frame is None:
                continue
            if name_frame.start_frame not in name_frames:
                name_frames[name_frame.start_frame] = [name_frame]
            else:
                name_frames[name_frame.start_frame].append(name_frame)

        frames = [PlayerNameAnalysisFrame(frame=frame, players=players) for frame, players in name_frames.items()]
        frames.sort(key=lambda frame: frame.frame)
        return PlayerNameAnalysisResult(frames=frames)
    
    def _make_name_item(self, items: list[(TrackableItem, int)]) -> PlayerNameAnalysisFrame:
        texts = []
        char_imgs = []
        for item in items:
            name = item[0]
            frame= item[1]
            img = self.reader.read(frame)
            name_img = img[name.xyxy[1]:name.xyxy[3],name.xyxy[0]:name.xyxy[2]]
            chars = self.ocr.get_text(name_img)
            if len(chars) > 0:
                text = to_str(chars)
                texts.append(text)
                char_imgs += [name_img[c.xyxy[1]:c.xyxy[3],c.xyxy[0]:c.xyxy[2]] for c in chars]
            else:
                char_imgs.append(name_img)

        name_text = likely_text(texts)
        stacked_image = hstack(images=char_imgs)
        #cv2.imshow(name_text, stacked_image)
        #cv2.waitKey(0)
        side = InkColor.likely_side(stacked_image, self.team_color, self.enemy_color)
        player = self._find_player(name_text, side)
        
        return PlayerNameItem(
            player=player,
            start_frame=items[0][1],
            end_frame=items[-1][1],
            track_id=items[0][0].track_id
        ) if player else None

    def _find_player(self, name: str, side: BattleSide) -> IkaPlayer:
        if side == BattleSide.TEAM and len(self.team_players) > 0:
            dists = [Levenshtein.ratio(name, p.name) for p in self.team_players]
            min_idx = np.argmax(dists)
            return self.team_players[min_idx] if dists[min_idx] > 0.3 else None
        elif side == BattleSide.ENEMY and len(self.enemy_players) > 0:
            dists = [Levenshtein.ratio(name, p.name) for p in self.enemy_players]
            min_idx = np.argmax(dists)
            return self.enemy_players[min_idx] if dists[min_idx] > 0.3 else None
        return None
