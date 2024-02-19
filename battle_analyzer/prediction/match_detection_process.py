from dataclasses import dataclass
from multiprocessing import Value
import numpy as np
from prediction.shared_memory import SharedMemory
from prediction.prediction_process import PredictionResultBase, run_prediction, toCpu
from prediction.frame import Frame
from models.detected_item import DetectedItem
from models.battle import MatchType

@dataclass
class MatchTypeItem(DetectedItem):
    match_type: MatchType
    
    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        match_type = MatchType(jc['match_type'])
        del jc['match_type']
        return cls(match_type=match_type, **jc)

@dataclass
class MatchDetectionFrame(Frame):
    match_type_item: MatchTypeItem
    match_color_items: list[DetectedItem]
    match_rate_item_menu_x: DetectedItem
    match_rate_item_update_x: DetectedItem
    
    @classmethod
    def from_json(cls, j):
        if j is None:
            print('')
        return cls(
            match_type_item= MatchTypeItem.from_json(j['match_type_item']) if j['match_type_item'] is not None else None,
            match_color_items=[DetectedItem.from_json(t) for t in j['match_color_items']],
            match_rate_item_menu_x=DetectedItem.from_json(j['match_rate_item_menu_x']) if j['match_rate_item_menu_x'] is not None else None,
            match_rate_item_update_x=DetectedItem.from_json(j['match_rate_item_update_x']) if j['match_rate_item_update_x'] is not None else None,
            frame=j['frame'],
            image=None
        )

@dataclass
class MatchDetectionResult(PredictionResultBase):
    frames: [MatchDetectionFrame]

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        frames = [MatchDetectionFrame.from_json(i) for i in jc['frames']]
        del jc['frames']
        return cls(
            frames=frames,
            **jc
        )

class SharedMatchDetectionResult(SharedMemory):
    SHM_NAME = 'shared_match'

def parse(pred, frame) -> MatchDetectionFrame:
    match_type_item = None
    match_color_items = []
    match_rate_item_menu_x = None
    match_rate_item_update_x = None

    for data in pred:
        xyxy, conf, cls = toCpu(data)
        
        if cls == 0: # match_color_player
            match_color_items.append(DetectedItem(xyxy=xyxy, conf=conf, cls=cls))
        elif cls == 1: # match_type_result_nawabari
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.REGULAR_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 2: # match_type_result_bankara
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.BANKARA_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 3: # match_type_result_x
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.X_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 4: # match_type_result_event
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.EVENT_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 5: # match_type_result_fes
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.FES_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 6: # match_type_result_priv
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.PRIV_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 7: # match_type_winlose_bankara
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.BANKARA_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 8: # match_type_winlose_x
            if match_type_item:
                return None
            match_type_item = MatchTypeItem(match_type=MatchType.X_MATCH, xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 9: # match_rate_update_x
            if match_rate_item_update_x:
                return None
            match_rate_item_update_x = DetectedItem(xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 10: # match_rate_update_event
            pass
        elif cls == 11: # match_rate_menu_x
            if match_rate_item_menu_x:
                return None
            match_rate_item_menu_x = DetectedItem(xyxy=xyxy, conf=conf, cls=cls)
        elif cls == 12: # match_rate_menu_event
            pass

    return MatchDetectionFrame(
        match_type_item=match_type_item,
        match_color_items=match_color_items,
        match_rate_item_menu_x=match_rate_item_menu_x,
        match_rate_item_update_x=match_rate_item_update_x,
        frame=frame,
        image=None
    )

def make_frame_result(pred, frame: int, img: np.ndarray) -> MatchDetectionFrame:
    f = parse(pred, frame)
    return f if f is not None else MatchDetectionFrame(
        match_type_item=None,
        match_color_items=[],
        match_rate_item_menu_x=None,
        match_rate_item_update_x=None,
        frame=frame,
        image=None
    )
    
def make_detection_completed(
    width: int,
    height: int,
    total_frames: int,
    start_frame: int,
    end_frame: int,
    frame_interval: int,
    frame_results: [MatchDetectionFrame],
    processing_time: int
   ) -> MatchDetectionResult:
    result = MatchDetectionResult(
        image_width=width,
        image_height=height,
        total_frames=total_frames,
        start_frame=start_frame,
        end_frame=end_frame,
        frame_interval=frame_interval,
        frames=frame_results,
        processing_time=processing_time
    )
 
    return result

def run_match_detection(
    battle_movie_path: str,
    match_model_path: str,
    frame_interval: int,
    device: str,
    process_id: int,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None,
    write_shared_memory: bool = True
):
    result = run_prediction(
        name='match',
        battle_movie_path=battle_movie_path,
        model_path=match_model_path,
        start_frame=start_frame,
        end_frame=end_frame,
        frame_interval=frame_interval,
        device=device,
        batch_size=batch_size,
        iou_threshold=0.25,
        conf_threshold=0.3,
        max_detections=100,
        make_frame_result_func=make_frame_result,
        make_prediction_completed_func=make_detection_completed
    )
    
    if write_shared_memory:
        SharedMatchDetectionResult.set_id(process_id)
        SharedMatchDetectionResult.write(result)
    
    return result
    