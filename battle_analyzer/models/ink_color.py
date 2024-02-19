import cv2
import numpy as np
from prediction.ikalamp_detection_process import IkalampDetectionFrame
from models.ikalamp import Ikalamp, IkalampState
from models.battle import BattleSide
from utils import hstack, MovieReader
from error import InternalError

class InkColor:
    def __init__(self,
        color: tuple,
    ) -> None:
       self.color = color

    def calc_distance(self, color) -> int:
        c1 = np.array(self.color)
        c2 = np.array(color.color)
        return np.sum(np.abs(c1 - c2))

    @classmethod  
    def create_from_ikalamp(cls, battle_movie_path: str, frames: list[IkalampDetectionFrame], side: BattleSide):
        reader = MovieReader(battle_movie_path)
        lamp_images = []
        for frame in frames:
            img = reader.read(frame.frame)
            lamps = []
            if side == BattleSide.TEAM and frame.team is not None:
                lamps = frame.team
            elif side == BattleSide.ENEMY and frame.enemy is not None:
                lamps = frame.enemy
            
            live_lamps = list(filter(lambda l: l.state == IkalampState.LIVE, lamps))
            if len(live_lamps) == 0:
                continue
            
            stacked_img = hstack(img, live_lamps)
            lamp_images.append(stacked_img)

        if len(lamp_images) == 0:
            return None

        total_image = hstack(images=lamp_images)
        colors, bins = cls.calc_dominat_colors(total_image)
        c =  colors[np.argmax(bins)]
        return cls((int(c[0]), int(c[1]), int(c[2])) )
    
    @classmethod
    def create_from_image(cls, image: np.ndarray):
        colors, bins = cls.calc_dominat_colors(image)
        c =  colors[np.argmax(bins)]
        color = (int(c[0]), int(c[1]), int(c[2])) 
        return cls(color)
    
    @classmethod
    def calc_dominat_colors(cls, img: np.ndarray, k: int=4) -> (list[tuple], list[int]):
        K = k
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(img.reshape(-1, 3).astype(np.float32), K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        return centers, np.bincount(labels.ravel())

    @staticmethod
    def likely_side(img: np.ndarray, team_color, enemy_color) -> BattleSide:
        colors, _ = InkColor.calc_dominat_colors(img)
        color_candidates = [InkColor(c) for c in colors]
        dist_team = min([color.calc_distance(team_color) for color in color_candidates])
        dist_enemy = min([color.calc_distance(enemy_color) for color in color_candidates])
        return BattleSide.TEAM if dist_team < dist_enemy else BattleSide.ENEMY
    
    @classmethod
    def from_json(cls, j):
        return cls(
            color=tuple(j['color'])
        )