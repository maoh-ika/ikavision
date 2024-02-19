from dataclasses import dataclass
from typing import TypeVar
import torch
from ultralytics import YOLO
from prediction.frame import Frame
from utils import MovieReader

T = TypeVar('T')

class FrameClassifier:
    def __init__(self,
        battle_movie_path: str,
        model_path: str,
        device: str,
        cls_to_value_map: dict[str,T]) -> None:
        dev = torch.device(device)
        self.model = YOLO(model_path)
        self.model.to(dev)
        self.battle_movie_path = battle_movie_path
        self.cls_to_value_map = cls_to_value_map

    def classify_most_likely(self, frames: list[Frame]) -> T:
        if len(frames) == 0:
            return None
        values = self.classify(frames)
        value_counts = {}
        for value in values.values():
            if value is None:
                continue
            if value not in value_counts:
                value_counts[value] = 1
            else:
                value_counts[value] += 1

        if len(values) == 0:
            return None

        value_counts = list(sorted(value_counts.items(), key=lambda x: x[1], reverse=True))
        return value_counts[0][0]

    def classify(self, frames: list[Frame]) -> dict[int,T]:
        reader = MovieReader(self.battle_movie_path)
        values = {}
        for frame in frames:
            if frame.image is None:
                img = reader.read(frame.frame)
            else:
                img = frame.image
            res = self.model.predict(img, verbose=False)[0]
            cls = res.names[res.probs.top1]
            values[frame.frame] = self.cls_to_value_map[cls]
        reader.release()
        return values