from dataclasses import dataclass
import torch
import numpy as np
from ultralytics import YOLO
from models.buki import SubWeapon
from models.ikalamp import IkalampState, Ikalamp
from prediction.frame import Frame
from prediction.ika_player_detection_process import IkaPlayerDetectionFrame
from prediction.frame_classifier import FrameClassifier
from utils import MovieReader

cls_weapon_map = {
    'splash_bomb': SubWeapon.SPLASH_BOMB,
    'kyuuban_bomb': SubWeapon.KYUUBAN_BOMB,
    'quick_bomb': SubWeapon.QUICK_BOMB,
    'sprinkler': SubWeapon.SPRINKLER,
    'splash_shield': SubWeapon.SPLASH_SHIELD,
    'tansan_bomb': SubWeapon.TANSAN_BOMB,
    'curling_bomb': SubWeapon.CURLING_BOMB,
    'robot_bomb': SubWeapon.ROBOT_BOMB,
    'jump_beacon': SubWeapon.JUMP_BEACON,
    'point_sensor': SubWeapon.POINT_SENSOR,
    'trap': SubWeapon.TRAP,
    'poison_mist': SubWeapon.POISON_MIST,
    'line_marker': SubWeapon.LINE_MARKER,
    'torpede': SubWeapon.TORPEDE
}

class SubWeaponFrameClassifier(FrameClassifier):
    def __init__(self,
        battle_movie_path: str,
        model_path: str,
        device: str) -> None:
        super().__init__(
            battle_movie_path=battle_movie_path,
            model_path=model_path,
            device=device,
            cls_to_value_map=cls_weapon_map)
