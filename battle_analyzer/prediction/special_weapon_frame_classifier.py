from dataclasses import dataclass
import torch
import numpy as np
from ultralytics import YOLO
from models.buki import SpecialWeapon
from models.ikalamp import IkalampState, Ikalamp
from prediction.frame import Frame
from prediction.ika_player_detection_process import IkaPlayerDetectionFrame
from prediction.frame_classifier import FrameClassifier
from utils import MovieReader

cls_weapon_map = {
    'kani_tank': SpecialWeapon.KANI_TANK,
    'syoku_wonder': SpecialWeapon.SYOKU_WONDER,
    'kyuuinki': SpecialWeapon.KYUUINKI,
    'energy_stand': SpecialWeapon.ENERGY_STAND,
    'hop_sonar': SpecialWeapon.HOP_SONAR,
    'same_ride': SpecialWeapon.SAME_RIDE,
    'decoy_tirashi': SpecialWeapon.DECOY_TIRASHI,
    'great_barrier': SpecialWeapon.GREAT_BARRIER,
    'ultra_shoot': SpecialWeapon.ULTRA_SHOOT,
    'megaphone_laser_51ch': SpecialWeapon.MEGAPHONE_LASER_51CH,
    'triple_tornade': SpecialWeapon.TRIPLE_TORNADE,
    'teioh_ika': SpecialWeapon.TEIOH_IKA,
    'multi_missile': SpecialWeapon.MULTI_MISSILE,
    'jet_pack': SpecialWeapon.JET_PACK,
    'amefurashi': SpecialWeapon.AMEFURASHI,
    'ultra_hanko': SpecialWeapon.ULTRA_HANKO,
    'nice_dama': SpecialWeapon.NICE_DAMA,
    'ultra_tyakuti': SpecialWeapon.ULTRA_TYAKUTI,
    'suminaga_sheet': SpecialWeapon.SUMINAGA_SHEET
}

class SpecialWeaponFrameClassifier(FrameClassifier):
    def __init__(self,
        battle_movie_path: str,
        model_path: str,
        device: str) -> None:
        super().__init__(
            battle_movie_path=battle_movie_path,
            model_path=model_path,
            device=device,
            cls_to_value_map=cls_weapon_map)
