import os
from dataclasses import dataclass
import cv2
from dotenv import load_dotenv
import torch
import threading
import queue
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from prediction.ikalamp_detection_process import make_frame_result as make_ikalamp_frame, make_detection_completed as make_ikalamp_result, IkalampDetectionFrame
from prediction.ika_player_detection_process import make_frame_result as make_ika_frame, make_detection_completed as make_ika_result, IkaPlayerDetectionFrame
from prediction.prediction_process import run_prediction, preprocess, postprocess

load_dotenv()

def draw_bbox(xyxy, label, cls, conf, annotator):
    label =  f'{label} {conf:.2f}'
    annotator.box_label(xyxy, label, color=colors(cls, True))

def draw_ikalamps(ikalamp_frame: IkalampDetectionFrame, annotator: Annotator):
    if ikalamp_frame.team is not None:
        for lamp in ikalamp_frame.team:
            draw_bbox(lamp.xyxy, lamp.state.name, lamp.state.value, lamp.conf, annotator)
    if ikalamp_frame.enemy is not None:
        for lamp in ikalamp_frame.enemy:
            draw_bbox(lamp.xyxy, lamp.state.name, lamp.state.value, lamp.conf, annotator)
    if ikalamp_frame.timer is not None:
        draw_bbox(ikalamp_frame.timer.xyxy, ikalamp_frame.timer.state.name, ikalamp_frame.timer.state.value, ikalamp_frame.timer.conf, annotator)
    
def draw_ika(ika_frame: IkaPlayerDetectionFrame, annotator: Annotator):
    for pos in ika_frame.positions:
        draw_bbox(pos.xyxy, f'{pos.form.name}_{pos.track_id}', pos.form.value, pos.conf, annotator)
    for name in ika_frame.names:
        draw_bbox(name.xyxy, 'name', name.cls, name.conf, annotator)

def draw_positions(ika_frame: IkaPlayerDetectionFrame, annotator: Annotator):
    for pos in ika_frame.positions:
        draw_bbox(pos.xyxy, f'{pos.form.name}_{pos.track_id}', pos.form.value, pos.conf, annotator)
    for name in ika_frame.names:
        draw_bbox(name.xyxy, 'name', name.cls, name.conf, annotator)

@dataclass
class InputFrame:
    frame: np.ndarray
    frame_number: int

# AIモデルによる推論実行のスレッド
class PredictionTread(threading.Thread):
    def __init__(
        self,
        name: str,
        model: str,
        result_queue: queue.Queue,
        frame_interval: int,
        make_frame_func,
        make_result_func) -> None:
        super().__init__(name=name)
        self.model = model
        self.result_queue = result_queue
        self.request_queue = queue.Queue()
        self.frame_interval = frame_interval
        self.make_frame_func = make_frame_func
        self.make_result_func = make_result_func
        self.shutdown_requested = False
    
    def add_frames(self, frames: list[InputFrame]):
        if len(frames) == 0:
            raise Exception('empty input')
        self.request_queue.put(frames)

    def run(self):
        while not self.shutdown_requested:
            frames = self.request_queue.get()
            images = list(map(lambda f: f.frame, frames))
            preds = self._predict(images)
            frame_results = []
            for idx, pred in enumerate(preds):
                frame_result = self.make_frame_func(pred, frames[idx].frame_number, images[idx])
                frame_results.append(frame_result)

            start_frame = frames[0].frame_number
            end_frame = frames[-1].frame_number
            total_frame = end_frame - start_frame + 1
            result = self.make_result_func(
                images[0].shape[1],
                images[-1].shape[0],
                total_frame,
                start_frame,
                end_frame,
                self.frame_interval,
                frame_results,
                0
            )
            self.result_queue.put(result)

    def _predict(self, frames: list[InputFrame]):
        raise Exception('no impl')
    
# オブジェクト検知モデル実行のスレッド
class DetectionThread(PredictionTread):
    def _predict(self, images: list[np.ndarray]):
        tensors = [preprocess(img, self.model.overrides['imgsz'], self.model.device, to_4d=False) for img in images]
        batch = torch.stack(tensors)
        preds = self.model.model(batch)
        return postprocess(preds, batch.shape[2:], images[0].shape, 0.25, 0.1, 100)

# オブジェクトトラッキングモデル実行のスレッド
class TrackingThread(PredictionTread):
    def _predict(self, images: list[np.ndarray]):
        return self.model.track(images, persist=True, conf=0.1, iou=0.25, verbose=False, tracker='bytetrack.yaml')

if __name__ == '__main__':
    
    cap = cv2.VideoCapture(0) # この環境ではキャプチャボードのデバイス番号は0
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():
        print('device not found')

    # ゲーム画面表示用ウィンドウ
    win_name = 'splatoon3'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 1920, 1080)
    
    frame_interval = 3
    device = torch.device('cuda')

    # イカランプ検出モデル
    ikalamp_model_path = os.environ.get('IKALAMP_MODEL_PATH')
    ikalamp_model = YOLO(ikalamp_model_path)
    ikalamp_model.to(device)
    ikalamp_result_queue = queue.Queue()
    ikalamp_thread = DetectionThread(
        'ikalamp',
        ikalamp_model,
        ikalamp_result_queue,
        frame_interval,
        make_ikalamp_frame,
        make_ikalamp_result
    )
    ikalamp_thread.start()
    
    # イカタコ検出モデル
    ika_model_path = os.environ.get('IKA_PLAYER_MODEL_PATH')
    ika_model = YOLO(ika_model_path)
    ika_model.to(device)
    ika_result_queue = queue.Queue()
    ika_thread = TrackingThread(
        'ika',
        ika_model,
        ika_result_queue,
        frame_interval,
        make_ika_frame,
        make_ika_result
    )
    ika_thread.start()

    # イカ検出モデル
    ika_model_path = os.environ.get('IKA_PLAYER_MODEL_PATH')
    ika_model = YOLO(ika_model_path)
    ika_model.to(device)
    ika_result_queue = queue.Queue()
    ika_thread = TrackingThread(
        'ika',
        ika_model,
        ika_result_queue,
        frame_interval,
        make_ika_frame,
        make_ika_result
    )
    ika_thread.start()

    # process stream

    batch_size = 1
    frame_number = 0
    while True:
        ret = cap.grab()
        if frame_number % frame_interval != 0:
            frame_number += 1
            continue
        ret, frame = cap.retrieve()
        if not ret:
            print('failed to read frame')
            break
            
        input_batch = []
        input_batch.append(InputFrame(frame, frame_number))

        # イカランプ検出スレッド実行 
        ikalamp_thread.add_frames(input_batch)
        
        # イカタコ検出スレッド実行 
        ika_thread.add_frames(input_batch)

        # 推論スレッドの処理完了待ち 
        ikalamp_result = ikalamp_result_queue.get()
        ika_result = ika_result_queue.get()

        # ゲーム画面にイカランプの枠線を書き込み
        ikalamp_frame = ikalamp_result.frames[0]
        ikalamp_annotator = Annotator(frame, line_width=1, example=str(ikalamp_model.model.names))
        draw_ikalamps(ikalamp_frame, ikalamp_annotator)
        
        # ゲーム画面にイカタコの枠線を書き込み
        ika_frame = ika_result.frames[0]
        ika_annotator = Annotator(frame, line_width=1, example=str(ika_model.model.names))
        draw_ika(ika_frame, ika_annotator)
        
        cv2.imshow(win_name, frame)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

        frame_number += 1

    cap.release()
    cv2.destroyAllWindows() 