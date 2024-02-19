from dataclasses import dataclass
from threading import Thread
from ultralytics import YOLO
import torch
import cv2
import numpy as np
from prediction.player_position_frame_analyzer import PlayerPositionAnalysisResult
from prediction.prediction_process import preprocess
from utils import class_to_dict 
from models.ika_player import IkaPlayerPosition, InkTank 
from models.detected_item import SegmentItem
from utils import bounding_box, MovieReader
from error import InternalError

@dataclass
class InkTankAnalysisFrame:
    main_player_ink: InkTank
    frame: int
    
    @classmethod
    def from_json(cls, j):
        return cls(
            main_player_ink=IkaPlayerPosition.from_json(j['main_player_position']),
            frame=j['frame'],
        )
    
@dataclass
class InkTankAnalysisResult:
    frames: list[InkTankAnalysisFrame] 
    
    @classmethod
    def from_json(cls, j):
        return cls(
            frames=[InkTankAnalysisFrame.from_json(t) for t in j['frames']],
        )
    
    def to_dict(self):
        return class_to_dict(self)

class InkTankFrameAnalyzer(Thread):
    def __init__(self,
            battle_movie_path: str,
            ink_tank_model_path: str,
            device: str
        ) -> None:
        super().__init__()
        dev = torch.device(device) 
        self.ink_tank_model = YOLO(ink_tank_model_path)
        self.ink_tank_model.to(dev)
        self.reader = MovieReader(battle_movie_path)
        self.player_position_result: PlayerPositionAnalysisResult = None
        self.result: InkTankAnalysisResult = None

    def analyze(self, player_position_result: PlayerPositionAnalysisResult) -> InkTankAnalysisResult:
        self.player_position_result = player_position_result
        self.start()

    def run(self):
        if self.player_position_result is None:
            raise InternalError('run must be called via create')
        ink_frames = []
        for pos_frame in self.player_position_result.frames:
            img = self.reader.read(pos_frame.frame)
            if pos_frame.main_player_position:
                main_ink = self._predict_ink_tank(img, pos_frame.main_player_position)
                if main_ink:
                    ink_frames.append(InkTankAnalysisFrame(main_player_ink=main_ink, frame=pos_frame.frame))

        self.result = InkTankAnalysisResult(frames=ink_frames)
    
    def _predict_ink_tank(self, img: np.ndarray, position: IkaPlayerPosition) -> InkTank:
        pos_img = img[position.xyxy[1]:position.xyxy[3],position.xyxy[0]:position.xyxy[2]] 
        #cv2.imshow('ee', pos_img)
        #cv2.waitKey(0)
        input = preprocess(pos_img, self.ink_tank_model.overrides['imgsz'], self.ink_tank_model.device)
        pred = self.ink_tank_model.predict(input, verbose=False)[0]
        if len(pred.boxes.data) == 0:
            return None

        consumed_mask = np.zeros([pos_img.shape[0], pos_img.shape[1]], np.uint8)
        consumed_conf = 1
        remaining_mask = np.zeros([pos_img.shape[0], pos_img.shape[1]], np.uint8)
        remaining_conf = 1
        for idx in range(len(pred.masks.data)):
            if pred.boxes.cls[idx] == 0:
                m = pred.masks.data[idx].cpu().numpy().astype('uint8')
                resized_mask = cv2.resize(m, (pos_img.shape[1], pos_img.shape[0]))
                consumed_mask =  cv2.bitwise_or(resized_mask, consumed_mask)
                consumed_conf = min(consumed_conf, float(pred.boxes.conf[idx]))
            elif pred.boxes.cls[idx] == 1:
                m = pred.masks.data[idx].cpu().numpy().astype('uint8')
                resized_mask = cv2.resize(m, (pos_img.shape[1], pos_img.shape[0]))
                remaining_mask =  cv2.bitwise_or(resized_mask, remaining_mask)
                remaining_conf = min(remaining_conf, float(pred.boxes.conf[idx]))

        consumed_mask = np.array(np.nonzero(consumed_mask))
        consumed_mask = consumed_mask[::-1]
        consumed_mask = np.transpose(consumed_mask)
        consumed_mask[:,0] += position.xyxy[0]
        consumed_mask[:,1] += position.xyxy[1]
        consumed_volume = consumed_mask.shape[0]

        remaining_mask = np.array(np.nonzero(remaining_mask))
        remaining_mask = remaining_mask[::-1]
        remaining_mask = np.transpose(remaining_mask)
        remaining_mask[:,0] += position.xyxy[0]
        remaining_mask[:,1] += position.xyxy[1]
        remaining_volume = remaining_mask.shape[0]
        if consumed_volume == 0 and remaining_volume == 0:
            return None
        ink_level = remaining_volume / (consumed_volume + remaining_volume)
        
        return InkTank(
            ink_level=ink_level,
            consumed=SegmentItem(xyxy=bounding_box(consumed_mask), conf=consumed_conf, cls=0, mask=consumed_mask) if consumed_volume > 0 else None,
            remaining=SegmentItem(xyxy=bounding_box(remaining_mask), conf=remaining_conf, cls=1, mask=remaining_mask) if remaining_volume > 0 else None,
        )
