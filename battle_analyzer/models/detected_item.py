from dataclasses import dataclass, field
import numpy as np

@dataclass
class DetectedItem:
    xyxy: [int]
    conf: float
    cls: int

    @property
    def width(self):
        return self.xyxy[2] - self.xyxy[0]
    
    @property
    def height(self):
        return self.xyxy[3] - self.xyxy[1]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            xyxy=j['xyxy'],
            conf=j['conf'],
            cls=j['cls'],
        )

@dataclass
class TrackableItem(DetectedItem):
    track_id: int

    @classmethod
    def from_json(cls, j):
        return cls(
            xyxy=j['xyxy'],
            conf=j['conf'],
            cls=j['cls'],
            track_id=j['track_id']
        )
    
@dataclass
class SegmentItem(DetectedItem):
    mask: np.ndarray

    @classmethod
    def from_json(cls, j):
        return cls(
            xyxy=j['xyxy'],
            conf=j['conf'],
            cls=j['cls'],
            mask=np.array(j['mask'])
        )