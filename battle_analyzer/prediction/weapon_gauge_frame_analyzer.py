from dataclasses import dataclass
import torch
import numpy as np
from ultralytics import YOLO
from models.buki import SubWeapon, SpecialWeapon
from prediction.frame import Frame
from prediction.sub_weapon_frame_classifier import SubWeaponFrameClassifier
from prediction.special_weapon_frame_classifier import SpecialWeaponFrameClassifier
from prediction.prediction_process import preprocess, postprocess, toCpu
from utils import MovieReader, are_overlapping

class WeaponGaugeFrameAnalyzer:
    def __init__(self,
        battle_movie_path: str,
        weapon_gauge_model_path: str,
        sub_weapon_classifier: SubWeaponFrameClassifier,
        sp_weapon_classifier: SpecialWeaponFrameClassifier,
        device: str) -> None:
        self.battle_movie_path = battle_movie_path
        self.gauge_model = YOLO(weapon_gauge_model_path)
        self.gauge_model.to(torch.device(device))
        self.sub_weapon_classifier = sub_weapon_classifier
        self.sp_weapon_classifier = sp_weapon_classifier

    def analyze_weapons(self, frames: list[Frame]) -> (SubWeapon, SpecialWeapon):
        sub_weapon_frames = []
        sp_weapon_frames = []

        reader = MovieReader(self.battle_movie_path)
        for frame in frames:
            img = reader.read(frame.frame)
            input = preprocess(img, self.gauge_model.overrides['imgsz'], self.gauge_model.device)
            preds = self.gauge_model.model(input)
            preds = postprocess(preds, input.shape[2:], img.shape, 0.25, 0.4, 100, agnostic=False)[0]

            is_dup = True
            gauge_xyxy = None 
            sub_xyxy = None
            sp_xyxy = None
            for data in preds:
                xyxy, conf, cls = toCpu(data)
                if cls == 0:
                    if gauge_xyxy is not None:
                        is_dup = False
                        break
                    gauge_xyxy = xyxy
                elif cls == 1:
                    if sub_xyxy is not None:
                        is_dup = False
                        break
                    sub_xyxy = xyxy
                elif cls == 2:
                    if sp_xyxy is not None:
                        is_dup = False
                        break
                    sp_xyxy = xyxy
            if not is_dup:
                continue
            if gauge_xyxy is None or sub_xyxy is None or sp_xyxy is None:
                continue
            
            if not are_overlapping(gauge_xyxy, sub_xyxy) or not are_overlapping(gauge_xyxy, sp_xyxy):
                continue

            weapon_img = img[sub_xyxy[1]:sub_xyxy[3],sub_xyxy[0]:sub_xyxy[2]]
            sub_weapon_frames.append(Frame(frame=frame.frame, image=weapon_img))
            sp_img = img[sp_xyxy[1]:sp_xyxy[3],sp_xyxy[0]:sp_xyxy[2]]
            sp_weapon_frames.append(Frame(frame=frame.frame, image=sp_img))

        sub_weapon = self.sub_weapon_classifier.classify_most_likely(sub_weapon_frames)
        sp_weapon = self.sp_weapon_classifier.classify_most_likely(sp_weapon_frames)

        reader.release()

        return (sub_weapon, sp_weapon)