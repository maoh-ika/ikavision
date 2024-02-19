from dataclasses import dataclass
from multiprocessing import Value
from prediction.shared_memory import SharedMemory
from prediction.prediction_process import PredictionResultBase, run_parallel
from prediction.frame import Frame
from models.ika_player import IkaPlayerPosition, IkaPlayerForm
from models.detected_item import TrackableItem

@dataclass
class IkaPlayerDetectionFrame(Frame):
    positions: list[IkaPlayerPosition]
    names: list[TrackableItem]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            positions=[IkaPlayerPosition.from_json(t) for t in j['positions']],
            names=[TrackableItem.from_json(t) for t in j['names']],
            frame=j['frame'],
            image=None
        )

@dataclass
class IkaPlayerDetectionResult(PredictionResultBase):
    frames: [IkaPlayerDetectionFrame]

    @classmethod
    def from_json(cls, j):
        return cls(
            image_width=j['image_width'],
            image_height=j['image_height'],
            total_frames=j['total_frames'],
            start_frame=j['start_frame'],
            end_frame=j['end_frame'],
            frame_interval=j['frame_interval'],
            frames=[IkaPlayerDetectionFrame.from_json(i) if i is not None else None for i in j['frames']],
            processing_time=j['processing_time'],
        )

class SharedIkaPlayerDetectionResult(SharedMemory):
    SHM_NAME = 'shared_ika_player'

def to_form(cls) -> IkaPlayerForm:
    if cls == 0: # ika_hito
        return IkaPlayerForm.HITO
    elif cls == 1: # ika_ika
        return IkaPlayerForm.IKA
    elif cls == 2: # ika_ikaroll
        return IkaPlayerForm.IKAROLL
    elif cls == 3: # ika_ikadash
        return IkaPlayerForm.IKADASH
    elif cls == 4: # ika_far
        return IkaPlayerForm.HITO_FAR
    elif cls in [5, 6, 7, 8, 9]: # ika_player_name, ika_player_name_death, ika_crown_fes_1, ika_crown_fes_2, ika_crown_x_1
        raise ValueError('invalid ika form value')
    elif cls == 10: # ika_hito_main
        return IkaPlayerForm.HITO_MAIN
    elif cls == 11: # ika_hito_sub
        return IkaPlayerForm.HITO_SUB
    elif cls == 12: # ika_hito_sp
        return IkaPlayerForm.HITO_SP
    else:
        raise ValueError('invalid ika form value')

def make_positions(pred) -> (list[IkaPlayerPosition], list[TrackableItem]):
    positions = []
    names = []
    for idx in range(len(pred.boxes.data)):
        x1 = int(pred.boxes.data[idx][0].cpu().numpy().astype('uint'))
        y1 = int(pred.boxes.data[idx][1].cpu().numpy().astype('uint'))
        x2 = int(pred.boxes.data[idx][2].cpu().numpy().astype('uint'))
        y2 = int(pred.boxes.data[idx][3].cpu().numpy().astype('uint'))
        conf = float(pred.boxes.conf[idx].cpu().numpy().astype('float'))
        cls = int(pred.boxes.cls[idx].cpu().numpy().astype('uint'))
        box = [x1, y1, x2, y2]
        track_id = int(pred.boxes.id[idx].cpu().numpy().astype('uint')) if pred.boxes.id is not None else None
        if cls in [5, 6, 7, 8, 9]: # ika_player_name, ika_player_name_death, ika_crown_fes_1, ika_crown_fes_2, ika_crown_x_1
            name = TrackableItem(xyxy=box, conf=conf, cls=cls, track_id=track_id)
            names.append(name)
        else:
            pos = IkaPlayerPosition(xyxy=box, form=to_form(cls), conf=conf, cls=cls, track_id=track_id)
            positions.append(pos)

    return positions, names

def make_frame_result(pred, frame: int, _) -> IkaPlayerDetectionFrame:
    positions, names = make_positions(pred)
    return IkaPlayerDetectionFrame(
        positions=positions,
        names=names,
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
    frame_results: [IkaPlayerDetectionFrame],
    processing_time: int
   ) -> IkaPlayerDetectionResult:
    result = IkaPlayerDetectionResult(
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

def run_ika_player_detection(
    battle_movie_path: str,
    ika_model_path: str,
    frame_interval: int,
    device: str,
    process_id: int,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None
):
    result = run_parallel(
        workers=4,
        name='ikaplayer',
        battle_movie_path=battle_movie_path,
        model_path=ika_model_path,
        start_frame=start_frame,
        end_frame=end_frame,
        frame_interval=frame_interval,
        device=device,
        batch_size=1,
        iou_threshold=0.25,
        conf_threshold=0.3,
        max_detections=100,
        make_frame_result_func=make_frame_result,
        make_prediction_completed_func=make_detection_completed,
        tracingEnabled=True
    )
    
    SharedIkaPlayerDetectionResult.set_id(process_id)
    SharedIkaPlayerDetectionResult.write(result)
    
    return result
    
if __name__ == '__main__':
    SharedIkaPlayerDetectionResult.reset()
    
    battle_movie_path = './videos/buki/2023070915221600-4CE9651EE88A979D41F24CE8D6EA1C23.mp4'
    result = run_ika_player_detection(
        battle_movie_path=battle_movie_path,
        ika_model_path='./models/ika/best.pt',
        start_frame=0,
        end_frame=2
    )
    
    ika_player_result = SharedIkaPlayerDetectionResult.read()
    