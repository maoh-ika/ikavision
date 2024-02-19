from dataclasses import dataclass
from multiprocessing import Value
from prediction.shared_memory import SharedMemory
from prediction.prediction_process import PredictionResultBase, toCpu, run_prediction 
from prediction.frame import Frame
from models.notification import NotificationType, Notification

@dataclass
class NotificationDetectionFrame(Frame):
    notifications: [Notification]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            notifications=[Notification.from_json(t) for t in j['notifications']],
            frame=j['frame'],
            image=None
        )

@dataclass
class NotificationDetectionResult(PredictionResultBase):
    frames: [NotificationDetectionFrame]

    @classmethod
    def from_json(cls, j):
        return cls(
            image_width=j['image_width'],
            image_height=j['image_height'],
            total_frames=j['total_frames'],
            start_frame=j['start_frame'],
            end_frame=j['end_frame'],
            frame_interval=j['frame_interval'],
            frames=[NotificationDetectionFrame.from_json(i) if i is not None else None for i in j['frames']],
            processing_time=j['processing_time'],
        )

class SharedNotificationDetectionResult(SharedMemory):
    SHM_NAME = 'shared_notification'

def make_notifications(pred) -> list[Notification]:
    notifications = []
    for data in pred:
        xyxy, conf, cls = toCpu(data)
        pos = Notification(xyxy=xyxy, type=NotificationType(cls), conf=conf, cls=cls)
        notifications.append(pos)

    return notifications

def make_frame_result(pred, frame: int, _) -> NotificationDetectionFrame:
    notifications = make_notifications(pred)
    return NotificationDetectionFrame(
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
    frame_results: list[NotificationDetectionFrame],
    processing_time: int
   ) -> NotificationDetectionResult:
    result = NotificationDetectionResult(
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

def run_notification_detection(
    battle_movie_path: str,
    notification_model_path: str,
    frame_interval: int,
    device: str,
    process_id: int,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None
):
    result = run_prediction(
        name='notification',
        battle_movie_path=battle_movie_path,
        model_path=notification_model_path,
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

    SharedNotificationDetectionResult.set_id(process_id) 
    SharedNotificationDetectionResult.write(result)
    
    return result

if __name__ == '__main__':
    SharedNotificationDetectionResult.reset()
    
    battle_movie_path = './videos/buki/2023070915221600-4CE9651EE88A979D41F24CE8D6EA1C23.mp4'
    result = run_notification_detection(
        battle_movie_path=battle_movie_path,
        notification_model_path='./models/notification/best.pt',
        start_frame=0,
        end_frame=4
    )

    result = SharedNotificationDetectionResult.read()
    print(result)