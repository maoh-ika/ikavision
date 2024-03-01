import os
from dataclasses import dataclass
import cv2
from dotenv import load_dotenv
import torch
import threading
import multiprocessing
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from prediction.ikalamp_detection_process import make_frame_result as make_ikalamp_frame, make_detection_completed as make_ikalamp_result, IkalampDetectionFrame, IkalampDetectionResult
from prediction.ika_player_detection_process import make_frame_result as make_ika_frame, make_detection_completed as make_ika_result, IkaPlayerDetectionFrame, IkaPlayerDetectionResult
from prediction.prediction_process import run_prediction, preprocess, postprocess
from prediction.player_position_frame_analyzer import PlayerPositionFrameAnalyzer, PlayerPositionAnalysisResult
from models.ika_player import IkaPlayerPosition

load_dotenv()

@dataclass
class State:
    ikalamp: IkalampDetectionResult = None
    ika: IkaPlayerDetectionResult = None
    main_player: PlayerPositionAnalysisResult = None

@dataclass
class InputFrame:
    frame: np.ndarray
    frame_number: int

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

def draw_main_player(img: np.ndarray, main_player_position: IkaPlayerPosition):
    if main_player_position:
        xyxy = main_player_position.xyxy
        cv2.rectangle(img, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (255, 0, 255), 3)

# AIモデルによる推論実行のプロセス
class PredictionProcess(multiprocessing.Process):
    def __init__(
        self,
        name: str,
        model_path: str,
        request_queue: multiprocessing.Queue,
        result_queue: multiprocessing.Queue,
        frame_interval: int,
        make_frame_func,
        make_result_func) -> None:
        super().__init__(name=name)
        self.model_path = model_path
        self.request_queue = request_queue
        self.result_queue = result_queue
        self.frame_interval = frame_interval
        self.make_frame_func = make_frame_func
        self.make_result_func = make_result_func
        self.shutdown_requested = False
    
    def run(self):
        model = YOLO(self.model_path)
        while not self.shutdown_requested:
            frames = self.request_queue.get()
            images = list(map(lambda f: f.frame, frames))
            preds = self._predict(model, images)
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

    def _predict(self, model: YOLO, frames: list[InputFrame]):
        raise Exception('no impl')
    
# オブジェクト検知モデル実行のプロセス
class DetectionProcess(PredictionProcess):
    def _predict(self, model: YOLO, images: list[np.ndarray]):
        tensors = [preprocess(img, model.overrides['imgsz'], model.device, to_4d=False) for img in images]
        batch = torch.stack(tensors)
        preds = model.model(batch)
        return postprocess(preds, batch.shape[2:], images[0].shape, 0.25, 0.1, 100)

# オブジェクトトラッキングモデル実行のプロセス
class TrackingProcess(PredictionProcess):
    def _predict(self, model: YOLO, images: list[np.ndarray]):
        return model.track(images, persist=True, conf=0.1, iou=0.25, verbose=False, tracker='bytetrack.yaml')

class ResultMonitorThread(threading.Thread):
    def __init__(self, state: State, result_queue: multiprocessing.Queue, update_func):
        super().__init__()
        self.state = state
        self.result_queue = result_queue
        self.update_func = update_func

    def run(self):
        while True:
            result = self.result_queue.get()
            self.update_func(self.state, result)

def update_frame(state: State, frame: np.ndarray):
    # ゲーム画面にイカランプの枠線を書き込み
    if state.ikalamp:
        ikalamp_frame = state.ikalamp.frames[0]
        ikalamp_annotator = Annotator(frame, line_width=1)
        draw_ikalamps(ikalamp_frame, ikalamp_annotator)
    
    # ゲーム画面にイカタコの枠線を書き込み
    if state.ika:
        ika_frame = state.ika.frames[0]
        ika_annotator = Annotator(frame, line_width=1)
        draw_ika(ika_frame, ika_annotator)

    # 自キャラの枠線を太線で協調表示
    if state.main_player and len(state.main_player.frames) == 1:
        draw_main_player(frame, state.main_player.frames[0].main_player_position)

if __name__ == '__main__':
    
    cap = cv2.VideoCapture(0) # この環境ではキャプチャボードのデバイス番号は0
    if not cap.isOpened():
        print('device not found')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    # ゲーム画面表示用ウィンドウ
    win_name = 'splatoon3'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 1920, 1080)
    
    frame_interval = frame_rate // 3
    device = torch.device('cuda')
    
    state = State()

    # イカランプ検出モデル
    ikalamp_model_path = os.environ.get('IKALAMP_MODEL_PATH')
    ikalamp_request_queue = multiprocessing.Queue()
    ikalamp_result_queue = multiprocessing.Queue()
    ikalamp_thread = DetectionProcess(
        'ikalamp',
        ikalamp_model_path,
        ikalamp_request_queue,
        ikalamp_result_queue,
        frame_interval,
        make_ikalamp_frame,
        make_ikalamp_result
    )
    ikalamp_thread.start()

    def _updateIkalamp(state: State, ikalamp_result: IkalampDetectionResult):
        state.ikalamp = ikalamp_result

    ikalamp_update_thread = ResultMonitorThread(state, ikalamp_result_queue, update_func=_updateIkalamp)
    ikalamp_update_thread.start()
    
    # イカタコ検出モデル
    ika_model_path = os.environ.get('IKA_PLAYER_MODEL_PATH')
    ika_request_queue = multiprocessing.Queue()
    ika_result_queue = multiprocessing.Queue()
    ika_thread = TrackingProcess(
        'ika',
        ika_model_path,
        ika_request_queue,
        ika_result_queue,
        frame_interval,
        make_ika_frame,
        make_ika_result
    )
    ika_thread.start()
    
    def _updateIka(state: State, ika_result: IkaPlayerDetectionResult):
        state.ika = ika_result
        # 操作キャラの位置を特定
        # ストリームは1フレームごとに処理するため動画でのバッチ処理に比べて精度は落ちる
        state.main_player = player_position_analyzer.analyze(state.ika)
    
    ika_update_thread = ResultMonitorThread(state, ika_result_queue, update_func=_updateIka)
    ika_update_thread.start()

    # 自キャラの位置情報の識別器
    player_position_analyzer = PlayerPositionFrameAnalyzer()

    # process stream

    batch_size = 1
    frame_number = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print('failed to read frame')
            break
        
        if frame_number % frame_interval != 0:
            frame_number += 1
            update_frame(state, frame)        
            cv2.imshow(win_name, frame)
            cv2.waitKey(1)
            continue
            
        input_batch = []
        input_batch.append(InputFrame(frame, frame_number))

        # イカランプ検出スレッド実行 
        ikalamp_request_queue.put(input_batch)
        # イカタコ検出スレッド実行 
        ika_request_queue.put(input_batch)

        update_frame(state, frame)        
        cv2.imshow(win_name, frame)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

        frame_number += 1

    cap.release()
    cv2.destroyAllWindows() 