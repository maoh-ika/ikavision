from dataclasses import dataclass
from multiprocessing import Value
import numpy as np
from prediction.shared_memory import SharedMemory
from prediction.prediction_process import PredictionResultBase, run_prediction 
from prediction.frame import Frame
from models.battle_indicator import BattleIndicator, BattleResult, ResultCount, IndicatorNotification, IndicatorNotificationType
from models.detected_item import DetectedItem
from models.battle import BattleWinLose

@dataclass
class BattleIndicatorDetectionFrame(Frame):
    indicator: BattleIndicator
    result: BattleResult
    notifications: list[IndicatorNotification]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            indicator=BattleIndicator.from_json(j['indicator']) if j['indicator'] is not None else None,
            result=BattleResult.from_json(j['result']) if j['result'] is not None else None,
            notifications=[IndicatorNotification.from_json(t) for t in j['notifications']],
            frame=j['frame'],
            image=None
        )

@dataclass
class BattleIndicatorDetectionResult(PredictionResultBase):
    frames: [BattleIndicatorDetectionFrame]

    @classmethod
    def from_json(cls, j):
        jc = j.copy()
        frames = [BattleIndicatorDetectionFrame.from_json(i) if i is not None else None for i in jc['frames']]
        del jc['frames']
        return cls(
            frames=frames,
            **jc
        )

class SharedBattleIndicatorDetectionResult(SharedMemory):
    SHM_NAME = 'shared_battle_indicator'

def parse(pred) -> (BattleIndicator, BattleResult, list[IndicatorNotification]):
    counts = [] 
    penalties = []
    result_counts = []
    occupancy = None
    lead_label = None
    judge = None
    kojudge = None
    win_lose = BattleWinLose.DRAW
    team_asari_counts = []
    player_asari_count = None
    player_asari_gachi = None
    nawabari_paint_point = None
    notifications = []

    pred = sorted(pred, key=lambda p: p[0]) # sort with x
    for *xyxy, conf, cls in pred:
        x1 = int(xyxy[0].cpu().numpy().astype('uint'))
        y1 = int(xyxy[1].cpu().numpy().astype('uint'))
        x2 = int(xyxy[2].cpu().numpy().astype('uint'))
        y2 = int(xyxy[3].cpu().numpy().astype('uint'))
        conf = float(conf.cpu().numpy().astype('float'))
        cls = int(cls.cpu().numpy().astype('uint'))
        box = [x1, y1, x2, y2]
        if cls == 0: # indicator_count
            counts.append(DetectedItem(xyxy=box, conf=conf, cls=cls))
        elif cls == 1: # indicator_area_occupancy
            occupancy = DetectedItem(xyxy=box, conf=conf, cls=cls)
        elif cls == 2: # indicator_lead
            lead_label = DetectedItem(xyxy=box, conf=conf, cls=cls)
        elif cls == 3: # indicator_count_lead
            notif = IndicatorNotification(type=IndicatorNotificationType.COUNT_LEAD, xyxy=box, conf=conf, cls=cls)
            notifications.append(notif)
        elif cls == 4: # indicator_count_behind
            notif = IndicatorNotification(type=IndicatorNotificationType.COUNT_BEHIND, xyxy=box, conf=conf, cls=cls)
            notifications.append(notif)
        elif cls == 5: # indicator_count_stop
            notif = IndicatorNotification(type=IndicatorNotificationType.COUNT_STOP, xyxy=box, conf=conf, cls=cls)
            notifications.append(notif)
        elif cls == 6: # indicator_count_stopped
            notif = IndicatorNotification(type=IndicatorNotificationType.COUNT_STOPPED, xyxy=box, conf=conf, cls=cls)
            notifications.append(notif)
        elif cls == 7: # indicator_area_secure
            notif = IndicatorNotification(type=IndicatorNotificationType.AREA_SECURE, xyxy=box, conf=conf, cls=cls)
            notifications.append(notif)
        elif cls == 8: # indicator_area_secured
            notif = IndicatorNotification(type=IndicatorNotificationType.AREA_SECURED, xyxy=box, conf=conf, cls=cls)
            notifications.append(notif)
        elif cls == 9: # indicator_penalty
            penalties.append(DetectedItem(xyxy=box, conf=conf, cls=cls))
        elif cls == 10: # indicator_result_win
            result_notif = IndicatorNotification(type=IndicatorNotificationType.RESULT_WIN, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
            win_lose = BattleWinLose.WIN
        elif cls == 11: # indicator_result_lose
            result_notif = IndicatorNotification(type=IndicatorNotificationType.RESULT_LOSE, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
            win_lose = BattleWinLose.LOSE
        elif cls == 12: # indicator_result_judge
            judge = DetectedItem(xyxy=box, conf=conf, cls=cls)
        elif cls == 13: # indicator_result_kojudge
            kojudge = DetectedItem(xyxy=box, conf=conf, cls=cls)
        elif cls == 14: # indicator_result_count
            result_counts.append(ResultCount(is_percent=False, is_knockout=False, xyxy=box, conf=conf, cls=cls))
        elif cls == 15: # indicator_result_percent
            result_counts.append(ResultCount(is_percent=True, is_knockout=False, xyxy=box, conf=conf, cls=cls))
        elif cls == 16: # indicator_result_knockout
            result_counts.append(ResultCount(is_percent=False, is_knockout=True, xyxy=box, conf=conf, cls=cls))
        elif cls == 17: # indicator_asari_team_total
            team_asari_counts.append(DetectedItem(xyxy=box, conf=conf, cls=cls))
        elif cls == 18: # indicator_asari_mine_total
            player_asari_count = DetectedItem(xyxy=box, conf=conf, cls=cls)
        elif cls == 19: # indicator_asari_mine_gachi
            player_asari_gachi = DetectedItem(xyxy=box, conf=conf, cls=cls)
        elif cls == 20: # indicator_asari_barrier_break
            result_notif = IndicatorNotification(type=IndicatorNotificationType.ASARI_BARRIER_BREAK, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 21: # indicator_asari_barrier_broken
            result_notif = IndicatorNotification(type=IndicatorNotificationType.ASARI_BARRIER_BROKEN, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 22: # indicator_asari_barrier_repair
            result_notif = IndicatorNotification(type=IndicatorNotificationType.ASARI_BARRIER_REPAIR, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 23: # indicator_asari_barrier_repaired
            result_notif = IndicatorNotification(type=IndicatorNotificationType.ASARI_BARRIER_REPAIRED, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 24: # indicator_hoko_get
            result_notif = IndicatorNotification(type=IndicatorNotificationType.HOKO_GET, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 25: # indicator_hoko_lost
            result_notif = IndicatorNotification(type=IndicatorNotificationType.HOKO_LOST, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 26: # indicator_hoko_robbed
            result_notif = IndicatorNotification(type=IndicatorNotificationType.HOKO_ROBBED, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 27: # indicator_hoko_stop
            result_notif = IndicatorNotification(type=IndicatorNotificationType.HOKO_STOP, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 28: # indicator_barrier_pass
            result_notif = IndicatorNotification(type=IndicatorNotificationType.BARRIER_PASS, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 29: # indicator_barrier_passed
            result_notif = IndicatorNotification(type=IndicatorNotificationType.BARRIER_PASSED, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 30: # indicator_nawabari_paintpoint
            nawabari_paint_point = DetectedItem(xyxy=box, conf=conf, cls=cls)
#            point_img = img[box[1]:box[3],box[0]:box[2]]
#            cv2.imshow('ss', point_img)
#            cv2.waitKey(0)

        elif cls == 31: # indicator_yagura_get
            result_notif = IndicatorNotification(type=IndicatorNotificationType.YAGURA_GET, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 32: # indicator_yagura_robbed
            result_notif = IndicatorNotification(type=IndicatorNotificationType.YAGURA_ROBBED, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 33: # indicator_yagura_return
            result_notif = IndicatorNotification(type=IndicatorNotificationType.YAGURA_RETURN, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 34: # indicator_yagura_returned
            result_notif = IndicatorNotification(type=IndicatorNotificationType.YAGURA_RETURNED, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 35: # indicator_yagura_barrier_reach
            result_notif = IndicatorNotification(type=IndicatorNotificationType.YAGURA_BARRIER_REACH, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)
        elif cls == 36: # indicator_yagura_barrier_reached
            result_notif = IndicatorNotification(type=IndicatorNotificationType.YAGURA_BARRIER_REACHED, xyxy=box, conf=conf, cls=cls)
            notifications.append(result_notif)

    is_result_frame = win_lose != BattleWinLose.DRAW and judge is not None and kojudge is not None and len(result_counts) == 2

    indicator = None
    result = None
    if is_result_frame:
        result = BattleResult(
            team_count=result_counts[0],
            enemy_count=result_counts[1],
            win_lose=win_lose
        )
    else:
        indicator = BattleIndicator(
            counts=counts,
            occupancy=occupancy,
            lead_label=lead_label,
            penalties=penalties,
            team_asari_counts=team_asari_counts,
            player_asari_count=player_asari_count,
            player_asari_gachi=player_asari_gachi,
            nawabari_paint_point=nawabari_paint_point
        )
    
    return indicator, result, notifications

def make_frame_result(pred, frame: int, img: np.ndarray) -> BattleIndicatorDetectionFrame:
    indicator, result, notifications = parse(pred)
    return BattleIndicatorDetectionFrame(
        indicator=indicator,
        result=result,
        notifications=notifications,
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
    frame_results: [BattleIndicatorDetectionFrame],
    processing_time: int
   ) -> BattleIndicatorDetectionResult:
    result = BattleIndicatorDetectionResult(
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

def run_battle_indicator_detection(
    battle_movie_path: str,
    battle_indicator_model_path: str,
    frame_interval: int,
    device: str,
    process_id: int,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None
):
    result = run_prediction(
        name='battle_indicator',
        battle_movie_path=battle_movie_path,
        model_path=battle_indicator_model_path,
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
    
    SharedBattleIndicatorDetectionResult.set_id(process_id)
    SharedBattleIndicatorDetectionResult.write(result)
    
    return result
    
if __name__ == '__main__':
    
    battle_movie_path = './videos/test/720p_30f_3mbps_192kbps.mp4'
    result = run_battle_indicator_detection(
        battle_movie_path=battle_movie_path,
        battle_indicator_model_path='./models/battle_indicator/area/best.pt',
        frame_interval=15,
        device='mps',
        start_frame=0
    )
    
    print(result) 