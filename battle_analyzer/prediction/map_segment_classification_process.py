from dataclasses import dataclass
from multiprocessing import Value
import numpy as np
import torch
import cv2
from ultralytics.data.augment import LetterBox
from prediction.shared_memory import SharedMemory
from prediction.prediction_process import PredictionResultBase, run_prediction
from prediction.frame import Frame

@dataclass
class MapSegmentClassificationFrame(Frame):
    segment_id: str
    
    @classmethod
    def from_json(cls, j):
        return cls(
            segment_id=j['segment_id'],
            frame=j['frame']
        )

@dataclass
class MapSegmentClassificationResult(PredictionResultBase):
    frames: [MapSegmentClassificationFrame]

    @classmethod
    def from_json(cls, j):
        return cls(
            image_width=j['image_width'],
            image_height=j['image_height'],
            total_frames=j['total_frames'],
            start_frame=j['start_frame'],
            end_frame=j['end_frame'],
            frame_interval=j['frame_interval'],
            frames=[MapSegmentClassificationFrame.from_json(i) if i is not None else None for i in j['frames']]
        )

class SharedMapSegmentClassificationResult(SharedMemory):
    SHM_NAME = 'shared_map_segment'

def make_frame_result(pred, frame: int) -> MapSegmentClassificationFrame:
    segment_id = pred.names[pred.probs.top1]
    return MapSegmentClassificationFrame(
        segment_id=segment_id,
        frame=frame
    )
    
def make_detection_completed(
    width: int,
    height: int,
    total_frames: int,
    start_frame: int,
    end_frame: int,
    frame_interval: int,
    frame_results: list[MapSegmentClassificationFrame],
    processing_time: int
   ) -> MapSegmentClassificationResult:
    result = MapSegmentClassificationResult(
        image_width=width,
        image_height=height,
        total_frames=total_frames,
        start_frame=start_frame,
        end_frame=end_frame,
        frame_interval=frame_interval,
        frames=frame_results,
        processing_time=processing_time
    )
    
    SharedMapSegmentClassificationResult.write(result)
    return result

def preprocess(img, size, device):
    img = LetterBox((size, size))(image=img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = img.transpose((2, 0, 1))
    img = torch.from_numpy(img)
    img = img.float()  # uint8 to fp16/32
    img /= 255  # 0 - 255 to 0.0 - 1.0
    img = img.to(device)
    return img.unsqueeze(0)

def run_map_segment_classifier(
    battle_movie_path: str,
    map_segment_model_path: str,
    shutdown_requested: Value,
    start_frame: int=0,
    end_frame: int=None,
    frame_interval: int=3,
    device: str='mps'
):
    result = run_prediction(
        name='mapsegment',
        battle_movie_path=battle_movie_path,
        model_path=map_segment_model_path,
        shutdown_requested=shutdown_requested,
        start_frame=start_frame,
        end_frame=end_frame,
        frame_interval=frame_interval,
        device=device,
        iou_threshold=0.25,
        conf_threshold=0.3,
        max_detections=1,
        make_frame_result_func=make_frame_result,
        make_prediction_completed_func=make_detection_completed,
        preprocess_func=preprocess
    )
   
    return result

if __name__ == '__main__':
    SharedMapSegmentClassificationResult.reset()
    
    shutdown_requested = Value('B', False)
    battle_movie_path = './videos/test/2023070915221600-4CE9651EE88A979D41F24CE8D6EA1C23.mp4'
    result = run_map_segment_classifier(
        battle_movie_path=battle_movie_path,
        map_segment_model_path='./models/map_segment/sumeshi/best.pt',
        shutdown_requested=shutdown_requested,
        start_frame=0,
        end_frame=4
    )

    result = SharedMapSegmentClassificationResult.read()
    print(result)