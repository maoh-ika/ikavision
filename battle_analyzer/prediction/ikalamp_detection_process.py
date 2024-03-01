from dataclasses import dataclass
from multiprocessing import Value
from prediction.shared_memory import SharedMemory
from prediction.prediction_process import PredictionResultBase, toCpu, run_prediction 
from prediction.frame import Frame
from models.ikalamp import Ikalamp, IkalampTimer, BattleSide, IkalampState, IkalampTimerState

@dataclass
class IkalampDetectionFrame(Frame):
    team: list[Ikalamp]
    enemy: list[Ikalamp]
    timer: IkalampTimer
    
    @classmethod
    def from_json(cls, j):
        return cls(
            team=[Ikalamp.from_json(t) for t in j['team']] if j['team'] else None,
            enemy=[Ikalamp.from_json(t) for t in j['enemy']] if j['enemy'] else None,
            timer=IkalampTimer.from_json(j['timer']) if j['timer'] else None,
            frame=j['frame'],
            image=None
        )

@dataclass
class IkalampDetectionResult(PredictionResultBase):
    frames: list[IkalampDetectionFrame]

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        frames = [IkalampDetectionFrame.from_json(i) if i is not None else None for i in jc['frames']]
        del jc['frames']
        return cls(
            frames=frames,
            **jc
        )

class SharedIkalampDetectionResult(SharedMemory):
    SHM_NAME = 'shared_ikalamp'

def make_lamps(pred) -> list[Ikalamp]:
    teams = []
    enemies = []
    timer = None
    team_member_count = 4
    enemy_member_count = 4
    total_objects = team_member_count + enemy_member_count + 1 # timer
    pred = sorted(pred, key=lambda p: p[4], reverse=True)[0:total_objects] # sort with conf
    if len(pred) != total_objects:
        return None
    pred = sorted(pred, key=lambda p: p[0]) # sort with x

    cur_side = BattleSide.TEAM
    team_ord = 0
    enemy_ord = 0
    for data in pred:
        xyxy, conf, cls = toCpu(data)
        if cls == 4: # timer:
            timer = IkalampTimer(state=IkalampTimerState.INTERVAL, xyxy=xyxy, conf=conf, cls=cls)
            cur_side = BattleSide.ENEMY
        else:
            if cur_side == BattleSide.TEAM:
                ikalamp = Ikalamp(side=cur_side, state=IkalampState(int(cls)), xyxy=xyxy, ord=team_ord, conf=conf, cls=cls)
                teams.append(ikalamp)
                team_ord += 1
            else:
                ikalamp = Ikalamp(side=cur_side, state=IkalampState(int(cls)), xyxy=xyxy, ord=enemy_ord, conf=conf, cls=cls)
                enemies.append(ikalamp)
                enemy_ord += 1

    if len(teams) != team_member_count or len(enemies) != enemy_member_count or timer is None:
        return None

    return teams, enemies, timer

def make_frame_result(pred, frame: int, img) -> IkalampDetectionFrame:
    lamps = make_lamps(pred)
    if lamps:
        return IkalampDetectionFrame(
            team=lamps[0],
            enemy=lamps[1],
            timer=lamps[2],
            frame=frame,
            image=img
        )
    else:
        return IkalampDetectionFrame(
            team=None,
            enemy=None,
            timer=None,
            frame=frame,
            image=img
        )
    
def make_detection_completed(
    width: int,
    height: int,
    total_frames: int,
    start_frame: int,
    end_frame: int,
    frame_interval: int,
    frame_results: list[IkalampDetectionFrame],
    processing_time: int
   ) -> IkalampDetectionResult:
    return IkalampDetectionResult(
        image_width=width,
        image_height=height,
        total_frames=total_frames,
        start_frame=start_frame,
        end_frame=end_frame,
        frame_interval=frame_interval,
        frames=frame_results,
        processing_time=processing_time
    )

def run_ikalamp_detection(
    battle_movie_path: str,
    ikalamp_model_path: str,
    frame_interval: int,
    device: str,
    process_id: int,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None,
    write_shared_memory: bool= True
):
    result = run_prediction(
        name='ikalamp',
        battle_movie_path=battle_movie_path,
        model_path=ikalamp_model_path,
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
        SharedIkalampDetectionResult.set_id(process_id)
        SharedIkalampDetectionResult.write(result)
    
    return result

if __name__ == '__main__':
    SharedIkalampDetectionResult.reset()
    
    shutdown_requested = Value('B', False)
    battle_movie_path = './videos/buki/2023070915221600-4CE9651EE88A979D41F24CE8D6EA1C23.mp4'
    lamps = run_ikalamp_detection(
        battle_movie_path=battle_movie_path,
        ikalamp_model_path='./models/ikalamp/best.pt',
        team_member_count=4,
        enemy_member_count= 4,
        has_timer=True,
        shutdown_requested=shutdown_requested,
        start_frame=0
    )
